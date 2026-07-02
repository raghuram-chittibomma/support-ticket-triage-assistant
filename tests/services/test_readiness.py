import pytest

from src.data_access import load_sample_tickets
from src.schemas import Category, TicketInput
from src.services.readiness import check_readiness

SAMPLE_TICKETS = load_sample_tickets()


def _to_ticket_input(raw: dict) -> TicketInput:
    return TicketInput(
        ticket_id=raw["ticket_id"],
        subject=raw["subject"],
        body=raw["body"],
        product_sku=raw.get("product_sku"),
        customer_persona=raw.get("customer_persona"),
        channel=raw.get("channel"),
    )


class TestCheckReadinessAgainstFixtures:
    @pytest.mark.parametrize("raw", SAMPLE_TICKETS, ids=[t["ticket_id"] for t in SAMPLE_TICKETS])
    def test_readiness_matches_expected_missing_fields(self, raw: dict):
        ticket = _to_ticket_input(raw)
        category = Category(raw["expected_category"])

        result = check_readiness(ticket, category)

        expected_missing = raw["expected_missing_fields"]
        assert sorted(result.missing_fields) == sorted(expected_missing)
        assert result.is_ready == (len(expected_missing) == 0)

    def test_at_least_one_ready_and_one_not_ready_ticket_exist(self):
        results = [
            check_readiness(_to_ticket_input(raw), Category(raw["expected_category"])) for raw in SAMPLE_TICKETS
        ]

        assert any(r.is_ready for r in results)
        assert any(not r.is_ready for r in results)


class TestCheckReadinessDeterminism:
    def test_same_input_yields_same_verdict(self):
        ticket = TicketInput(subject="Wi-Fi issue", body="My speaker keeps dropping Wi-Fi.")

        first = check_readiness(ticket, Category.WIFI_NETWORK)
        second = check_readiness(ticket, Category.WIFI_NETWORK)

        assert first == second
        assert first.is_ready is False
        assert first.missing_fields == ["router_band", "firmware_version"]

    def test_complete_ticket_is_ready(self):
        ticket = TicketInput(
            subject="Wi-Fi issue",
            body="I'm on the 5GHz band and running firmware version 2.0.",
        )

        result = check_readiness(ticket, Category.WIFI_NETWORK)

        assert result.is_ready is True
        assert result.missing_fields == []

    def test_category_with_no_required_fields_is_always_ready(self):
        ticket = TicketInput(subject="General question", body="What colors does this come in?")

        result = check_readiness(ticket, Category.GENERAL_QUESTION)

        assert result.is_ready is True
        assert result.missing_fields == []
