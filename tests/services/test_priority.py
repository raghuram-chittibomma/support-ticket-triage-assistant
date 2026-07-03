import pytest

from src.data_access import load_sample_tickets
from src.schemas import Priority, TicketInput
from src.services.priority import detect_escalation_language, estimate_priority

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


class TestEstimatePriorityAgainstFixtures:
    @pytest.mark.parametrize("raw", SAMPLE_TICKETS, ids=[t["ticket_id"] for t in SAMPLE_TICKETS])
    def test_priority_matches_expected(self, raw: dict):
        ticket = _to_ticket_input(raw)

        priority, reason = estimate_priority(ticket)

        assert priority == Priority(raw["expected_priority"])
        assert isinstance(reason, str) and reason

    def test_all_four_priority_levels_are_represented(self):
        results = {estimate_priority(_to_ticket_input(raw))[0] for raw in SAMPLE_TICKETS}

        assert results == {Priority.URGENT, Priority.HIGH, Priority.MEDIUM, Priority.LOW}


class TestEstimatePriorityRulePrecedence:
    def test_same_input_yields_same_result(self):
        ticket = TicketInput(subject="Burning smell", body="There is a burning smell from my amp.")

        first = estimate_priority(ticket)
        second = estimate_priority(ticket)

        assert first == second

    def test_safety_keyword_is_urgent_even_with_low_signal_language(self):
        ticket = TicketInput(
            subject="Question about my amp",
            body="I'm curious what's causing the burning smell coming from my amp — is it worth worrying about?",
        )

        priority, reason = estimate_priority(ticket)

        assert priority == Priority.URGENT
        assert "burning smell" in reason

    def test_total_failure_with_deadline_is_urgent(self):
        ticket = TicketInput(
            subject="Speaker dead",
            body="My speaker won't turn on and I need this resolved by my return window closing Friday.",
        )

        priority, _ = estimate_priority(ticket)

        assert priority == Priority.URGENT

    def test_total_failure_alone_is_high(self):
        ticket = TicketInput(subject="Speaker dead", body="My speaker won't turn on at all.")

        priority, _ = estimate_priority(ticket)

        assert priority == Priority.HIGH

    def test_escalation_language_is_high(self):
        ticket = TicketInput(
            subject="Still broken",
            body="I've called multiple times about this and nothing has been fixed.",
        )

        priority, _ = estimate_priority(ticket)

        assert priority == Priority.HIGH

    def test_informational_question_is_low(self):
        ticket = TicketInput(subject="Quick question", body="How do I clean the speaker grille?")

        priority, _ = estimate_priority(ticket)

        assert priority == Priority.LOW

    def test_unclassified_ongoing_problem_defaults_to_medium(self):
        ticket = TicketInput(
            subject="Odd noise",
            body="My amp has been making a strange clicking noise for the past few days.",
        )

        priority, reason = estimate_priority(ticket)

        assert priority == Priority.MEDIUM
        assert "default" in reason


class TestEstimatePriorityKeywordFalsePositiveRegressions:
    """Regression tests for word-boundary matching (independent Code Reviewer subagent finding
    on PR #40): short keywords like "shock" or "dent" must not match inside unrelated words."""

    def test_shockproof_does_not_trigger_safety_urgent(self):
        ticket = TicketInput(
            subject="Packaging quality",
            body="The box says it is shockproof but the corner was a bit dented in shipping.",
        )

        priority, reason = estimate_priority(ticket)

        assert priority != Priority.URGENT
        assert "shock" not in reason

    def test_identify_does_not_trigger_dent_low_signal(self):
        ticket = TicketInput(
            subject="Odd noise",
            body=(
                "My amp has been making a strange clicking noise for the past few days and "
                "I cannot identify the source."
            ),
        )

        priority, _ = estimate_priority(ticket)

        assert priority == Priority.MEDIUM

    def test_from_scratch_does_not_trigger_scratch_low_signal(self):
        ticket = TicketInput(
            subject="Sound issue",
            body="I want to reset my speaker from scratch and start over to see if that helps.",
        )

        priority, _ = estimate_priority(ticket)

        assert priority == Priority.MEDIUM

    def test_standalone_dent_keyword_still_matches(self):
        ticket = TicketInput(
            subject="Subwoofer arrived damaged",
            body="The cabinet itself has a visible dent on the front panel.",
        )

        priority, reason = estimate_priority(ticket)

        assert priority == Priority.LOW
        assert "dent" in reason

    def test_standalone_shock_keyword_still_matches(self):
        ticket = TicketInput(
            subject="Amp issue",
            body="I got a mild shock when I touched the metal casing of my amp.",
        )

        priority, reason = estimate_priority(ticket)

        assert priority == Priority.URGENT
        assert "shock" in reason


class TestDetectEscalationLanguage:
    """Public helper reused by src/services/human_review.py."""

    def test_returns_matched_keyword_when_present(self):
        result = detect_escalation_language(
            "Still broken", "I've called multiple times about this and nothing has changed."
        )

        assert result == "called multiple times"

    def test_returns_none_when_absent(self):
        result = detect_escalation_language("Quick question", "How do I clean the speaker grille?")

        assert result is None
