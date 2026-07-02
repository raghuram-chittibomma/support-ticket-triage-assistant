import pytest
from pydantic import ValidationError

from src.schemas import Category, Priority, ReadinessResult, Reference, TicketInput, TriageResult


class TestTicketInput:
    def test_minimal_construction_generates_ticket_id(self):
        ticket = TicketInput(subject="Speaker won't turn on", body="It just stopped working today.")

        assert ticket.ticket_id is not None
        assert ticket.ticket_id.startswith("TCK-GEN-")
        assert ticket.product_sku is None
        assert ticket.customer_persona is None
        assert ticket.channel is None
        assert ticket.submitted_at is None

    def test_explicit_ticket_id_is_preserved(self):
        ticket = TicketInput(ticket_id="TCK-0001", subject="Subject", body="Body")

        assert ticket.ticket_id == "TCK-0001"

    def test_full_construction(self):
        ticket = TicketInput(
            subject="Wi-Fi reconnect issue",
            body="My speaker won't reconnect after the update.",
            product_sku="SUM1-ACT",
            customer_persona="returning-customer",
            channel="email",
        )

        assert ticket.product_sku == "SUM1-ACT"
        assert ticket.channel == "email"

    def test_empty_body_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TicketInput(subject="Subject", body="")

    def test_empty_subject_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TicketInput(subject="", body="Body")

    def test_missing_required_fields_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TicketInput(subject="Subject only")  # type: ignore[call-arg]

    def test_invalid_channel_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TicketInput(subject="Subject", body="Body", channel="carrier-pigeon")  # type: ignore[arg-type]


class TestEnums:
    def test_category_round_trips_taxonomy_strings(self):
        assert Category("Wi-Fi / Network Connectivity") == Category.WIFI_NETWORK
        assert Category.WIFI_NETWORK.value == "Wi-Fi / Network Connectivity"

    def test_category_rejects_unknown_value(self):
        with pytest.raises(ValueError):
            Category("Not A Real Category")

    def test_priority_round_trips_values(self):
        assert Priority("Urgent") == Priority.URGENT
        assert {p.value for p in Priority} == {"Urgent", "High", "Medium", "Low"}


class TestReadinessResultAndReference:
    def test_readiness_result_defaults_to_empty_missing_fields(self):
        result = ReadinessResult(is_ready=True)

        assert result.missing_fields == []

    def test_reference_construction(self):
        ref = Reference(doc_id="KB-WIFI-004", title="Wi-Fi troubleshooting", excerpt="Power-cycle the device...")

        assert ref.doc_id == "KB-WIFI-004"


class TestTriageResult:
    def test_full_construction(self):
        result = TriageResult(
            category=Category.WIFI_NETWORK,
            category_confidence=0.92,
            category_explanation="Ticket mentions Wi-Fi reconnect after firmware update.",
            priority=Priority.HIGH,
            priority_reason="Complete loss of connectivity (won't connect at all).",
            readiness=ReadinessResult(is_ready=True, missing_fields=[]),
            likely_issue="Speaker lost its Wi-Fi network configuration after a firmware update.",
            suggested_next_action="Power-cycle the speaker and re-run network setup in the app.",
            suggested_response="Thanks for reaching out - please try power-cycling your speaker...",
            references=[Reference(doc_id="KB-WIFI-004", title="Wi-Fi reconnect issues", excerpt="...")],
            confidence_level="high",
            human_review_required=False,
            human_review_reason=None,
        )

        assert result.category == Category.WIFI_NETWORK
        assert result.references[0].doc_id == "KB-WIFI-004"

    def test_category_confidence_out_of_range_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TriageResult(
                category=Category.GENERAL_QUESTION,
                category_confidence=1.5,
                category_explanation="x",
                priority=Priority.LOW,
                priority_reason="x",
                readiness=ReadinessResult(is_ready=True),
                likely_issue="x",
                suggested_next_action="x",
                suggested_response="x",
                confidence_level="low",
                human_review_required=False,
            )

    def test_invalid_confidence_level_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TriageResult(
                category=Category.GENERAL_QUESTION,
                category_confidence=0.5,
                category_explanation="x",
                priority=Priority.LOW,
                priority_reason="x",
                readiness=ReadinessResult(is_ready=True),
                likely_issue="x",
                suggested_next_action="x",
                suggested_response="x",
                confidence_level="super-high",  # type: ignore[arg-type]
                human_review_required=False,
            )
