"""Deterministic human-review decision logic. See #21 and
docs/01_architecture/DATA_MODEL.md Section 13.

An ordered, explainable rule list (first matching rule wins) — no LLM call. Consumes
already-computed `priority`, `confidence_level`, and `readiness`, plus a direct escalation-
language check against the ticket text so escalation reliably triggers review independent
of which priority tier the ticket landed in.
"""

from src.schemas import Priority, ReadinessResult, TicketInput
from src.services.confidence import ConfidenceLevel
from src.services.priority import detect_escalation_language


def evaluate_human_review(
    ticket: TicketInput,
    priority: Priority,
    confidence_level: ConfidenceLevel,
    readiness: ReadinessResult,
) -> tuple[bool, str | None]:
    """Return (human_review_required, human_review_reason) for the given ticket/signals.

    Rule precedence (first match wins): Urgent priority > escalation language > low
    confidence > medium confidence + not ready > not required. See DATA_MODEL.md Section 13.
    """
    if priority == Priority.URGENT:
        return (
            True,
            "Ticket priority is Urgent (safety-related or deadline-critical); all Urgent "
            "tickets require human review regardless of other signals.",
        )

    escalation_match = detect_escalation_language(ticket.subject, ticket.body)
    if escalation_match:
        return True, f"Escalation language detected ('{escalation_match}')."

    if confidence_level == "low":
        return True, "Overall confidence in this triage result is low."

    if confidence_level == "medium" and not readiness.is_ready:
        return (
            True,
            "Confidence is medium and the ticket is missing information needed to act "
            "confidently.",
        )

    return False, None
