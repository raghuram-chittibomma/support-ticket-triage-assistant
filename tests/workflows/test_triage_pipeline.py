"""Integration tests for the full triage pipeline. Per #22's acceptance criteria: run the
full pipeline against data/sample/tickets.json, asserting deterministic fields exactly and
LLM-backed fields for shape/presence only (never asserting a "correct" LLM opinion — the
LLM is faked here to always agree with the fixture's ground-truth category, isolating this
test from real classification accuracy, which belongs to the evaluation scenario suite, #26).
"""

import json

import pytest

from src.data_access import load_sample_tickets
from src.llm import OpenAILLMClient
from src.retrieval import KeywordKBRetriever
from src.schemas import Category, Priority, TicketInput, TriageResult
from src.workflows.triage_pipeline import run_triage_pipeline

SAMPLE_TICKETS = load_sample_tickets()


class ScriptedLLMClient:
    """A fake LLMClient that always classifies as the given ground-truth category and
    always produces a well-formed, non-fabricating draft — good enough to exercise the full
    pipeline's wiring deterministically, without making real network calls or asserting
    anything about actual model quality (that's the evaluation suite's job, #26)."""

    def __init__(self, expected_category: Category):
        self.expected_category = expected_category
        self.calls: list[tuple[str, str]] = []

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        if "Choose exactly one category" in system_prompt:
            return json.dumps(
                {
                    "category": self.expected_category.value,
                    "explanation": f"This matches the {self.expected_category.value} category.",
                }
            )
        return json.dumps(
            {
                "likely_issue": "The customer is experiencing the issue described in the ticket body.",
                "suggested_next_action": "Review the ticket details and respond with tailored guidance.",
                "suggested_response": "Thanks for reaching out — we're looking into this for you.",
            }
        )


def _to_ticket_input(raw: dict) -> TicketInput:
    return TicketInput(
        ticket_id=raw["ticket_id"],
        subject=raw["subject"],
        body=raw["body"],
        product_sku=raw.get("product_sku"),
        customer_persona=raw.get("customer_persona"),
        channel=raw.get("channel"),
    )


class TestRunTriagePipelineAgainstFixtures:
    @pytest.mark.parametrize("raw", SAMPLE_TICKETS, ids=[t["ticket_id"] for t in SAMPLE_TICKETS])
    def test_pipeline_produces_a_complete_schema_valid_result(self, raw: dict):
        ticket = _to_ticket_input(raw)
        expected_category = Category(raw["expected_category"])
        llm_client = ScriptedLLMClient(expected_category)

        result = run_triage_pipeline(ticket, llm_client=llm_client, retriever=KeywordKBRetriever())

        assert isinstance(result, TriageResult)

        # Deterministic fields: asserted exactly against the fixture's ground truth.
        assert result.category == expected_category
        assert result.priority == Priority(raw["expected_priority"])
        assert sorted(result.readiness.missing_fields) == sorted(raw["expected_missing_fields"])
        assert result.readiness.is_ready == (len(raw["expected_missing_fields"]) == 0)

        # LLM-backed fields: asserted for shape/presence only, per #22's acceptance criteria
        # and TEST_STRATEGY.md — never for a "correct" opinion, since the LLM is faked here.
        assert 0.0 <= result.category_confidence <= 1.0
        assert result.category_explanation
        assert result.likely_issue
        assert result.suggested_next_action
        assert result.suggested_response
        assert isinstance(result.references, list)

        # Confidence/human-review are deterministic *given* the upstream signals above, so
        # their possible values are constrained even though the underlying classifier
        # confidence numbers come from the (faked) LLM path.
        assert result.confidence_level in ("high", "medium", "low")
        assert isinstance(result.human_review_required, bool)
        if result.human_review_required:
            assert result.human_review_reason
        else:
            assert result.human_review_reason is None

    def test_llm_client_is_called_for_both_classification_and_drafting(self):
        raw = SAMPLE_TICKETS[0]
        ticket = _to_ticket_input(raw)
        llm_client = ScriptedLLMClient(Category(raw["expected_category"]))

        run_triage_pipeline(ticket, llm_client=llm_client, retriever=KeywordKBRetriever())

        # Exactly one classification call and one drafting call — no redundant LLM calls
        # (see NFR5, interactive-demo latency).
        assert len(llm_client.calls) == 2


class TestRunTriagePipelineDefaults:
    def test_default_retriever_is_used_when_not_provided(self):
        raw = next(t for t in SAMPLE_TICKETS if t["expected_category"] == Category.WIFI_NETWORK.value)
        ticket = _to_ticket_input(raw)
        llm_client = ScriptedLLMClient(Category.WIFI_NETWORK)

        result = run_triage_pipeline(ticket, llm_client=llm_client)

        # The default KeywordKBRetriever should find at least one Wi-Fi article for a
        # well-formed Wi-Fi ticket, proving the default wasn't silently skipped in favor of
        # e.g. an accidentally-empty retriever.
        assert len(result.references) > 0

    def test_default_llm_client_propagates_missing_api_key_error(self):
        ticket = TicketInput(subject="Wi-Fi issue", body="My speaker keeps dropping Wi-Fi.")

        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            run_triage_pipeline(ticket, llm_client=OpenAILLMClient(api_key=""), retriever=KeywordKBRetriever())


class TestRunTriagePipelineDeterminism:
    def test_same_input_yields_same_result(self):
        raw = SAMPLE_TICKETS[0]
        ticket = _to_ticket_input(raw)
        expected_category = Category(raw["expected_category"])

        first = run_triage_pipeline(
            ticket, llm_client=ScriptedLLMClient(expected_category), retriever=KeywordKBRetriever()
        )
        second = run_triage_pipeline(
            ticket, llm_client=ScriptedLLMClient(expected_category), retriever=KeywordKBRetriever()
        )

        assert first == second
