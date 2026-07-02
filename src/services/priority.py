"""Deterministic priority estimation. See docs/01_architecture/DATA_MODEL.md Sections 3-4.

No LLM call. An ordered rule list is evaluated top to bottom; the first matching rule wins
and its name/matched keyword is returned as `priority_reason` for explainability.
"""

from src.schemas import Priority, TicketInput

SAFETY_KEYWORDS = [
    "burning smell",
    "smoke",
    "electrical smell",
    "shock",
    "sparks",
    "caught fire",
    "fire hazard",
]

TOTAL_FAILURE_KEYWORDS = [
    "won't turn on",
    "won't power on",
    "doesn't turn on",
    "no sound at all",
    "won't connect",
    "can't connect",
    "stopped connecting",
    "not connecting at all",
    "won't pair",
    "completely dead",
    "not working at all",
    "no power at all",
]

DEADLINE_KEYWORDS = [
    "return window",
    "return deadline",
    "need this resolved by",
    "before my return period ends",
]

ESCALATION_KEYWORDS = [
    "called multiple times",
    "contacted you before",
    "spoken to someone already",
    "very frustrated",
    "this is unacceptable",
    "third time",
    "charged twice",
    "charged me twice",
    "double charged",
]

# Informational/administrative/cosmetic signals. Per DATA_MODEL.md Section 3, Low covers
# "general product question, minor cosmetic defect, 'how do I...' questions" — these keyword
# phrases capture that intent without being tied to any one category.
LOW_SIGNAL_KEYWORDS = [
    "is it worth",
    "is that a safe",
    "is that a reasonable",
    "wondering if",
    "not sure if",
    "not sure how",
    "curious what",
    "curious how",
    "how do i",
    "how long does",
    "want to register",
    "would like to return",
    "requesting a return",
    "check on",
    "question about",
    "should i",
    "is it safe to",
    "trying to figure out",
    "instructions aren't very clear",
    "beat up",
    "haven't opened it yet",
    "don't think i want to keep",
    "still have the receipt",
    "dent",
    "dented",
    "scratch",
    "scuffed",
    "cosmetic",
]


def _first_match(text: str, keywords: list[str]) -> str | None:
    for keyword in keywords:
        if keyword in text:
            return keyword
    return None


def _ticket_text(ticket: TicketInput) -> str:
    return f"{ticket.subject} {ticket.body}".lower()


def estimate_priority(ticket: TicketInput) -> tuple[Priority, str]:
    """Return the deterministic (priority, priority_reason) for a ticket.

    Rule precedence (first match wins): Urgent > High > Low(informational/cosmetic) > Medium
    (default). See DATA_MODEL.md Section 3 for the rule descriptions and Section 4a for the
    keyword lists.
    """
    text = _ticket_text(ticket)

    safety_match = _first_match(text, SAFETY_KEYWORDS)
    if safety_match:
        return Priority.URGENT, f"Safety-related language detected ('{safety_match}')."

    failure_match = _first_match(text, TOTAL_FAILURE_KEYWORDS)
    deadline_match = _first_match(text, DEADLINE_KEYWORDS)
    if failure_match and deadline_match:
        return (
            Priority.URGENT,
            f"Complete loss of function ('{failure_match}') combined with a "
            f"return/shipping deadline mention ('{deadline_match}').",
        )

    if failure_match:
        return Priority.HIGH, f"Complete loss of function detected ('{failure_match}')."

    escalation_match = _first_match(text, ESCALATION_KEYWORDS)
    if escalation_match:
        return Priority.HIGH, f"Escalation language detected ('{escalation_match}')."

    low_match = _first_match(text, LOW_SIGNAL_KEYWORDS)
    if low_match:
        return (
            Priority.LOW,
            f"Informational, administrative, or cosmetic language detected ('{low_match}').",
        )

    return (
        Priority.MEDIUM,
        "No urgent, high, or low-priority signal detected; treated as an intermittent or "
        "partial issue by default.",
    )
