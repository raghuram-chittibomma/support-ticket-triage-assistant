from src.schemas import Priority, ReadinessResult, TicketInput
from src.services.human_review import evaluate_human_review

READY = ReadinessResult(is_ready=True, missing_fields=[])
NOT_READY = ReadinessResult(is_ready=False, missing_fields=["firmware_version"])


def _ticket(subject: str = "Question", body: str = "Just a routine question about my speaker.") -> TicketInput:
    return TicketInput(subject=subject, body=body)


class TestEvaluateHumanReviewFlaggedCases:
    def test_urgent_priority_is_always_flagged(self):
        required, reason = evaluate_human_review(_ticket(), Priority.URGENT, "high", READY)

        assert required is True
        assert "Urgent" in reason

    def test_urgent_priority_flagged_even_with_high_confidence_and_ready(self):
        """Story #36 AC: safety-related language always flags review regardless of other
        signals — Urgent priority is only reached via safety/deadline rules (priority.py)."""
        required, _ = evaluate_human_review(_ticket(), Priority.URGENT, "high", READY)

        assert required is True

    def test_urgent_priority_reason_wins_even_when_confidence_is_also_low(self):
        """Regression test from code review: pins down that the Urgent rule's early return
        takes precedence and its reason is the one surfaced, not the low-confidence reason,
        when both conditions happen to be true simultaneously."""
        required, reason = evaluate_human_review(_ticket(), Priority.URGENT, "low", NOT_READY)

        assert required is True
        assert "Urgent" in reason
        assert "confidence" not in reason.lower()

    def test_escalation_language_flagged_even_with_high_priority_confidence_and_ready(self):
        ticket = _ticket(
            subject="Still not fixed",
            body="I've called multiple times about this and nothing has changed.",
        )

        required, reason = evaluate_human_review(ticket, Priority.HIGH, "high", READY)

        assert required is True
        assert "Escalation language" in reason

    def test_low_confidence_is_flagged_regardless_of_priority_and_readiness(self):
        required, reason = evaluate_human_review(_ticket(), Priority.LOW, "low", READY)

        assert required is True
        assert "low" in reason.lower()

    def test_medium_confidence_and_not_ready_is_flagged(self):
        required, reason = evaluate_human_review(_ticket(), Priority.MEDIUM, "medium", NOT_READY)

        assert required is True
        assert "medium" in reason.lower()
        assert "missing information" in reason.lower()


class TestEvaluateHumanReviewNotFlaggedCases:
    def test_high_confidence_ready_low_priority_is_not_flagged(self):
        required, reason = evaluate_human_review(_ticket(), Priority.LOW, "high", READY)

        assert required is False
        assert reason is None

    def test_medium_confidence_but_ready_is_not_flagged(self):
        required, reason = evaluate_human_review(_ticket(), Priority.MEDIUM, "medium", READY)

        assert required is False
        assert reason is None

    def test_high_priority_without_escalation_language_is_not_automatically_flagged(self):
        ticket = _ticket(body="My speaker won't turn on at all.")

        required, _ = evaluate_human_review(ticket, Priority.HIGH, "high", READY)

        assert required is False


class TestEvaluateHumanReviewDeterminism:
    def test_same_input_yields_same_result(self):
        ticket = _ticket()

        first = evaluate_human_review(ticket, Priority.MEDIUM, "medium", NOT_READY)
        second = evaluate_human_review(ticket, Priority.MEDIUM, "medium", NOT_READY)

        assert first == second
