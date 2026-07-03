import json

from src.schemas import Category, Reference, TicketInput
from src.services.response_drafter import DraftResult, draft_response


class FakeLLMClient:
    def __init__(self, response: str):
        self.response = response
        self.calls: list[dict] = []

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return self.response


def _draft_json(
    likely_issue: str = "The speaker is losing its Wi-Fi connection after a firmware update.",
    suggested_next_action: str = "Confirm the customer's router band and firmware version.",
    suggested_response: str = "Sorry about the trouble! Please power-cycle your speaker and re-run network setup.",
) -> str:
    return json.dumps(
        {
            "likely_issue": likely_issue,
            "suggested_next_action": suggested_next_action,
            "suggested_response": suggested_response,
        }
    )


def _ticket() -> TicketInput:
    return TicketInput(
        subject="Speaker won't reconnect to Wi-Fi",
        body="My speaker stopped reconnecting to Wi-Fi after the last firmware update.",
        product_sku="SUM1-ACT",
    )


def _reference() -> Reference:
    return Reference(
        doc_id="KB-WIFI-004",
        title="Resolving Wi-Fi reconnect issues after firmware updates",
        excerpt="Power-cycle the device, confirm the router band, then re-run network setup.",
    )


class TestDraftResponseGroundedCase:
    def test_clean_response_citing_a_retrieved_doc_id_passes_through_unchanged(self):
        llm_client = FakeLLMClient(
            _draft_json(
                suggested_response=(
                    "Sorry about the trouble! Please power-cycle your speaker and re-run "
                    "network setup from the companion app (KB-WIFI-004). Let us know if that "
                    "resolves it."
                )
            )
        )

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert isinstance(result, DraftResult)
        assert "KB-WIFI-004" in result.suggested_response
        assert result.likely_issue
        assert result.suggested_next_action
        assert len(llm_client.calls) == 1

    def test_clean_response_with_no_doc_id_citation_passes_through_unchanged(self):
        expected = _draft_json(suggested_response="Sorry about the trouble! Please try power-cycling your speaker.")
        llm_client = FakeLLMClient(expected)

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert result == DraftResult.model_validate_json(expected)

    def test_markdown_fenced_json_is_parsed_correctly(self):
        expected = _draft_json()
        llm_client = FakeLLMClient(f"```json\n{expected}\n```")

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert result == DraftResult.model_validate_json(expected)

    def test_prompt_includes_ticket_and_reference_doc_ids(self):
        llm_client = FakeLLMClient(_draft_json())
        ticket = _ticket()
        reference = _reference()

        draft_response(ticket, Category.WIFI_NETWORK, [reference], llm_client)

        user_prompt = llm_client.calls[0]["user_prompt"]
        assert ticket.subject in user_prompt
        assert ticket.body in user_prompt
        assert reference.doc_id in user_prompt


class TestDraftResponseFabricationGuard:
    def test_fabricated_doc_id_in_response_triggers_fallback(self):
        llm_client = FakeLLMClient(
            _draft_json(
                suggested_response="As explained in our detailed guide (KB-MADE-UP-999), please try resetting the device."
            )
        )

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert "KB-MADE-UP-999" not in result.suggested_response
        assert _reference().title in result.suggested_response

    def test_fabricated_doc_id_in_likely_issue_triggers_fallback(self):
        """The guard scans all three fields, not just suggested_response — a fabricated
        citation smuggled into likely_issue must also fall back to the safe default draft."""
        llm_client = FakeLLMClient(_draft_json(likely_issue="Likely related to (KB-FAKE-123) as documented."))

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert "KB-FAKE-123" not in result.likely_issue
        assert _reference().title in result.suggested_response

    def test_fabricated_doc_id_with_no_references_triggers_generic_fallback(self):
        llm_client = FakeLLMClient(_draft_json(suggested_response="Please see (KB-NONEXISTENT-001) for details."))

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [], llm_client)

        assert "KB-NONEXISTENT-001" not in result.suggested_response
        assert "follow up" in result.suggested_response.lower()

    def test_empty_llm_response_triggers_fallback(self):
        llm_client = FakeLLMClient("   ")

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert result.suggested_response
        assert _reference().title in result.suggested_response

    def test_malformed_json_triggers_fallback(self):
        llm_client = FakeLLMClient("not valid json at all")

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert _reference().title in result.suggested_response

    def test_missing_field_triggers_fallback(self):
        llm_client = FakeLLMClient(json.dumps({"likely_issue": "Something.", "suggested_response": "A reply."}))

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert _reference().title in result.suggested_response

    def test_empty_string_field_triggers_fallback(self):
        llm_client = FakeLLMClient(_draft_json(suggested_next_action=""))

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert _reference().title in result.suggested_response

    def test_null_field_triggers_fallback_instead_of_literal_none_string(self):
        """Regression test from code review: `str(None)` would otherwise produce the literal
        text "None", which is non-empty and would silently pass through into TriageResult."""
        llm_client = FakeLLMClient(
            json.dumps(
                {
                    "likely_issue": None,
                    "suggested_next_action": "Follow up with the customer.",
                    "suggested_response": "A reply.",
                }
            )
        )

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert _reference().title in result.suggested_response
        assert result.likely_issue != "None"

    def test_clean_response_with_no_references_and_no_citation_passes_through(self):
        expected = _draft_json(suggested_response="Thanks for reaching out, here is some general guidance.")
        llm_client = FakeLLMClient(expected)

        result = draft_response(_ticket(), Category.GENERAL_QUESTION, [], llm_client)

        assert result == DraftResult.model_validate_json(expected)


class TestDraftResponseFabricationGuardRegressions:
    """Regression tests carried over from PR #42's independent Code Reviewer subagent
    findings: the fabrication guard must not depend on the fabricated citation matching the
    exact case or the exact "KB-XXX-NNN" numeric-suffix shape of real doc_ids."""

    def test_lowercase_fabricated_citation_is_caught(self):
        llm_client = FakeLLMClient(_draft_json(suggested_response="See our guide (kb-madeup-999) for help."))

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert "kb-madeup-999" not in result.suggested_response.lower()
        assert _reference().title in result.suggested_response

    def test_fabricated_citation_with_no_numeric_suffix_is_caught(self):
        llm_client = FakeLLMClient(
            _draft_json(suggested_response="Please consult (KB-TROUBLESHOOTING-GUIDE) for full steps.")
        )

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert "KB-TROUBLESHOOTING-GUIDE" not in result.suggested_response
        assert _reference().title in result.suggested_response

    def test_fabricated_citation_with_no_numeric_suffix_and_no_references_is_caught(self):
        llm_client = FakeLLMClient(_draft_json(suggested_response="Please see (kb-nonexistent) for details."))

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [], llm_client)

        assert "kb-nonexistent" not in result.suggested_response.lower()
        assert "follow up" in result.suggested_response.lower()

    def test_legitimately_cited_doc_id_in_different_case_is_not_flagged(self):
        expected = _draft_json(suggested_response="Please see our guide (kb-wifi-004) for the steps to follow.")
        llm_client = FakeLLMClient(expected)

        result = draft_response(_ticket(), Category.WIFI_NETWORK, [_reference()], llm_client)

        assert result == DraftResult.model_validate_json(expected)
