"""Response drafting: an LLMClient call that drafts a customer response grounded in
retrieved references. See docs/01_architecture/ARCHITECTURE.md and #19.

The LLM is instructed never to cite a doc_id beyond what was retrieved, but instructions
alone are not a guarantee — per .skills/rag-retrieval-design-review.md ("no fabricated
citations"), the response is also checked deterministically after generation: if it
mentions any KB-style doc_id that wasn't actually retrieved, the whole response is replaced
with a safe, deterministic fallback rather than shipping a fabricated citation.
"""

import re

from src.llm import LLMClient
from src.schemas import Category, Reference, TicketInput

# Case-insensitive, and deliberately loose about trailing shape (no required numeric
# suffix) — the goal is to catch anything that *looks like* a KB doc_id citation, not just
# ones that mimic today's "KB-XXX-NNN" convention exactly. A stricter pattern (e.g.
# requiring a trailing "-\d+") would let a fabricated citation like "(KB-TROUBLESHOOTING-
# GUIDE)" through completely undetected.
_DOC_ID_PATTERN = re.compile(r"\bKB-[A-Za-z0-9-]+\b", re.IGNORECASE)


def _build_system_prompt() -> str:
    return (
        "You are drafting a customer support reply for NorthPeak Audioworks, a home audio "
        "equipment company. Write a short, professional, ready-to-send reply that directly "
        "addresses the customer's stated issue. If knowledge-base references are provided, "
        "ground your answer in them and you may cite a doc_id in parentheses, e.g. "
        "(KB-WIFI-004) — but you must NEVER invent, guess, or reference a doc_id that was "
        "not explicitly provided to you. If no references are provided, respond helpfully "
        "in general terms and do not cite any doc_id at all. Respond with only the reply "
        "text, no preamble."
    )


def _build_user_prompt(ticket: TicketInput, category: Category, references: list[Reference]) -> str:
    lines = [
        f"Ticket category: {category.value}",
        f"Subject: {ticket.subject}",
        f"Body: {ticket.body}",
    ]
    if references:
        lines.append("")
        lines.append("Available knowledge-base references (only cite these doc_ids, if any):")
        for reference in references:
            lines.append(f"- {reference.doc_id}: {reference.title} — {reference.excerpt}")
    else:
        lines.append("")
        lines.append("No knowledge-base references were found for this ticket. Do not cite any doc_id.")
    return "\n".join(lines)


def _fallback_response(references: list[Reference]) -> str:
    if references:
        titles = "; ".join(reference.title for reference in references)
        return (
            "Thanks for reaching out about this. Based on similar cases, our guidance on "
            f"{titles} should help — a member of our support team will follow up shortly "
            "with more detail specific to your situation."
        )
    return (
        "Thanks for reaching out — we've received your message, and a member of our "
        "support team will follow up shortly with more detail."
    )


def draft_response(
    ticket: TicketInput,
    category: Category,
    references: list[Reference],
    llm_client: LLMClient,
) -> str:
    # Compared case-insensitively so a legitimately-cited real doc_id isn't flagged just
    # because the model wrote it in a different case than it was given.
    allowed_doc_ids = {reference.doc_id.upper() for reference in references}

    raw_response = llm_client.complete(
        system_prompt=_build_system_prompt(),
        user_prompt=_build_user_prompt(ticket, category, references),
    ).strip()

    if not raw_response:
        return _fallback_response(references)

    cited_doc_ids = {match.upper() for match in _DOC_ID_PATTERN.findall(raw_response)}
    fabricated_doc_ids = cited_doc_ids - allowed_doc_ids
    if fabricated_doc_ids:
        return _fallback_response(references)

    return raw_response
