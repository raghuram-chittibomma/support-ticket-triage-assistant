import pytest

from src.data_access import load_sample_tickets
from src.schemas import Category, TicketInput
from src.services.missing_info import REQUIRED_FIELDS_BY_CATEGORY, get_missing_fields

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


class TestGetMissingFieldsAgainstFixtures:
    """Every sample ticket's expected_missing_fields must match get_missing_fields exactly.

    This is the primary regression guard tying data/sample/tickets.json to the rule
    implementation, per docs/01_architecture/DATA_MODEL.md Section 4 and ADR-002.
    """

    @pytest.mark.parametrize("raw", SAMPLE_TICKETS, ids=[t["ticket_id"] for t in SAMPLE_TICKETS])
    def test_matches_expected_missing_fields(self, raw: dict):
        ticket = _to_ticket_input(raw)
        category = Category(raw["expected_category"])

        actual = get_missing_fields(ticket, category)

        assert sorted(actual) == sorted(raw["expected_missing_fields"])

    def test_fixtures_cover_every_category(self):
        categories_in_fixtures = {t["expected_category"] for t in SAMPLE_TICKETS}
        all_categories = {c.value for c in Category}

        assert categories_in_fixtures == all_categories

    def test_fixtures_include_at_least_one_complete_and_incomplete_ticket_per_rule_category(self):
        for category, required_fields in REQUIRED_FIELDS_BY_CATEGORY.items():
            if not required_fields:
                continue
            tickets_for_category = [t for t in SAMPLE_TICKETS if t["expected_category"] == category.value]
            assert any(t["expected_missing_fields"] == [] for t in tickets_for_category), (
                f"No complete (ready) fixture ticket for {category.value}"
            )
            assert any(t["expected_missing_fields"] for t in tickets_for_category), (
                f"No incomplete fixture ticket for {category.value}"
            )


class TestGetMissingFieldsDeterminism:
    def test_same_input_yields_same_result(self):
        ticket = TicketInput(subject="Wi-Fi issue", body="My speaker keeps dropping Wi-Fi.")

        first = get_missing_fields(ticket, Category.WIFI_NETWORK)
        second = get_missing_fields(ticket, Category.WIFI_NETWORK)

        assert first == second == ["router_band", "firmware_version"]

    def test_categories_without_required_fields_are_always_ready(self):
        ticket = TicketInput(subject="Random question", body="No relevant details at all.")

        assert get_missing_fields(ticket, Category.SETUP_INSTALLATION) == []
        assert get_missing_fields(ticket, Category.GENERAL_QUESTION) == []

    def test_keyword_match_is_case_insensitive(self):
        ticket = TicketInput(subject="Wi-Fi", body="I'm on the 5GHZ band running FIRMWARE VERSION 2.0.")

        assert get_missing_fields(ticket, Category.WIFI_NETWORK) == []
