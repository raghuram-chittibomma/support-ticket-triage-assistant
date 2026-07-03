import pytest

from pydantic import ValidationError

from src.schemas import Category, Priority, ReadinessResult, Reference, TriageResult
from src.ui.app import build_ticket_input, triage_from_form
from src.ui.formatting import format_triage_result


def _sample_result(*, human_review_required: bool = False) -> TriageResult:
    return TriageResult(
        category=Category.WIFI_NETWORK,
        category_confidence=0.9,
        category_explanation="Wi-Fi connectivity issue after a firmware update.",
        priority=Priority.HIGH,
        priority_reason="Complete loss of function detected ('won't connect').",
        readiness=ReadinessResult(is_ready=False, missing_fields=["router_band", "firmware_version"]),
        likely_issue="The speaker lost its Wi-Fi connection after updating firmware.",
        suggested_next_action="Confirm the customer's router band and firmware version.",
        suggested_response="Thanks for reaching out — please power-cycle your speaker and re-run network setup.",
        references=[
            Reference(
                doc_id="KB-WIFI-004",
                title="Resolving Wi-Fi reconnect issues after firmware updates",
                excerpt="Power-cycle the device, confirm the router band, then re-run network setup.",
            )
        ],
        confidence_level="medium",
        human_review_required=human_review_required,
        human_review_reason="Confidence is medium and the ticket is missing information." if human_review_required else None,
    )


class TestFormatTriageResult:
    def test_includes_all_nine_story_fields(self):
        rendered = format_triage_result(_sample_result())

        assert "## Category" in rendered
        assert "## Priority" in rendered
        assert "## Readiness" in rendered
        assert "## Likely issue" in rendered
        assert "## Suggested next action" in rendered
        assert "## Draft customer response" in rendered
        assert "## References" in rendered
        assert "## Overall confidence" in rendered
        assert "## Human review" in rendered
        assert "KB-WIFI-004" in rendered

    def test_human_review_flagged_case_shows_reason(self):
        rendered = format_triage_result(_sample_result(human_review_required=True))

        assert "human review required" in rendered.lower()
        assert "missing information" in rendered.lower()


class TestBuildTicketInput:
    def test_optional_fields_omitted_when_blank(self):
        ticket = build_ticket_input("Subject", "Body", "", "", "")

        assert ticket.subject == "Subject"
        assert ticket.body == "Body"
        assert ticket.product_sku is None
        assert ticket.customer_persona is None
        assert ticket.channel is None

    def test_optional_fields_included_when_provided(self):
        ticket = build_ticket_input("S", "B", "SUM1-ACT", "returning-customer", "email")

        assert ticket.product_sku == "SUM1-ACT"
        assert ticket.customer_persona == "returning-customer"
        assert ticket.channel == "email"


class TestTriageFromForm:
    def test_empty_subject_returns_error_without_calling_pipeline(self):
        called = False

        def fake_pipeline(_ticket):
            nonlocal called
            called = True
            return _sample_result()

        result = triage_from_form("", "Body text", "", "", "", run_pipeline=fake_pipeline)

        assert "Subject is required" in result
        assert called is False

    def test_empty_body_returns_error_without_calling_pipeline(self):
        called = False

        def fake_pipeline(_ticket):
            nonlocal called
            called = True
            return _sample_result()

        result = triage_from_form("Subject", "   ", "", "", "", run_pipeline=fake_pipeline)

        assert "Body is required" in result
        assert called is False

    def test_success_path_renders_pipeline_result(self):
        def fake_pipeline(ticket):
            assert ticket.subject == "Wi-Fi issue"
            return _sample_result()

        result = triage_from_form("Wi-Fi issue", "Speaker keeps dropping.", "", "", "", run_pipeline=fake_pipeline)

        assert "Wi-Fi / Network Connectivity" in result
        assert "Draft customer response" in result

    def test_missing_api_key_surfaces_configuration_error(self):
        from src.llm import MissingAPIKeyError

        def fake_pipeline(_ticket):
            raise MissingAPIKeyError("OPENAI_API_KEY is not set.")

        result = triage_from_form("S", "B", "", "", "", run_pipeline=fake_pipeline)

        assert "Configuration error" in result
        assert "OPENAI_API_KEY" in result

    def test_unexpected_pipeline_error_surfaces_friendly_message(self):
        def fake_pipeline(_ticket):
            raise RuntimeError("upstream service unavailable")

        result = triage_from_form("S", "B", "", "", "", run_pipeline=fake_pipeline)

        assert "Unexpected error" in result
        assert "upstream service unavailable" in result

    def test_invalid_channel_from_build_ticket_input_surfaces_validation_error(self):
        with pytest.raises(ValidationError):
            build_ticket_input("S", "B", "", "", "carrier-pigeon")


class TestBuildDemo:
    def test_demo_builds_without_error(self):
        from src.ui.app import build_demo

        demo = build_demo()

        assert demo is not None
