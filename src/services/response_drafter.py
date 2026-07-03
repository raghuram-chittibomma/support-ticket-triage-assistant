"""Response drafting: a single LLMClient call that produces a diagnosis (`likely_issue`), a
recommended next step for the support agent (`suggested_next_action`), and a ready-to-send
customer reply (`suggested_response`) grounded in retrieved references. See
docs/01_architecture/ARCHITECTURE.md and #19/#22.

`likely_issue` and `suggested_next_action` have no dedicated backlog item of their own —
`PRODUCT_BRIEF.md`'s FR8 only lists them as part of the aggregate `TriageResult` — so they are
produced here, in the same LLM call as the customer-facing reply, rather than via a second LLM
call. All three pieces of content require the same contextual understanding of the ticket, and
NFR5 (interactive-demo latency) favors one call per ticket over two.

The LLM is instructed never to cite a doc_id beyond what was retrieved, but instructions alone
are not a guarantee — per .skills/rag-retrieval-design-review.md ("no fabricated citations"),
the parsed output is also checked deterministically after generation: if ANY field mentions a
KB-style doc_id that wasn't actually retrieved, or the response can't be parsed at all, the
whole draft is replaced with a safe, deterministic fallback rather than shipping a fabricated
citation or a malformed result.
"""

import json
import re

from pydantic import BaseModel

from src.llm import LLMClient
from src.llm.utils import strip_markdown_code_fence
from src.schemas import Category, Reference, TicketInput

# Case-insensitive, and deliberately loose about trailing shape (no required numeric
# suffix) — the goal is to catch anything that *looks like* a KB doc_id citation, not just
# ones that mimic today's "KB-XXX-NNN" convention exactly. A stricter pattern (e.g.
# requiring a trailing "-\d+") would let a fabricated citation like "(KB-TROUBLESHOOTING-
# GUIDE)" through completely undetected.
_DOC_ID_PATTERN = re.compile(r"\bKB-[A-Za-z0-9-]+\b", re.IGNORECASE)


class DraftResult(BaseModel):
    likely_issue: str
    suggested_next_action: str
    suggested_response: str


def _build_system_prompt() -> str:
    return (
        "You are triaging a customer support ticket for NorthPeak Audioworks, a home audio "
        "equipment company. Respond with ONLY a JSON object of the form "
        '{"likely_issue": "<one or two sentence diagnosis of what is likely going on>", '
        '"suggested_next_action": "<one short, actionable next step for the SUPPORT AGENT '
        'handling this ticket, not the customer>", "suggested_response": "<a short, '
        "professional, ready-to-send reply that directly addresses the customer's stated "
        'issue>"}. Do not include any text outside the JSON object.\n\n'
        "If knowledge-base references are provided, ground suggested_response in them and "
        "you may cite a doc_id in parentheses there, e.g. (KB-WIFI-004) — but you must NEVER "
        "invent, guess, or reference a doc_id that was not explicitly provided to you, in any "
        "field. If no references are provided, respond helpfully in general terms in "
        "suggested_response and do not cite any doc_id anywhere."
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


def _fallback_response_text(references: list[Reference]) -> str:
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


def _fallback_draft(references: list[Reference]) -> DraftResult:
    return DraftResult(
        likely_issue=(
            "Unable to automatically determine the likely issue from the ticket text; a "
            "support agent should review it directly."
        ),
        suggested_next_action="Manually review the ticket details and follow up with the customer directly.",
        suggested_response=_fallback_response_text(references),
    )


def _parse_draft_response(raw: str, references: list[Reference]) -> DraftResult:
    try:
        data = json.loads(strip_markdown_code_fence(raw))
        likely_issue = str(data["likely_issue"] or "").strip()
        suggested_next_action = str(data["suggested_next_action"] or "").strip()
        suggested_response = str(data["suggested_response"] or "").strip()
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return _fallback_draft(references)

    if not likely_issue or not suggested_next_action or not suggested_response:
        return _fallback_draft(references)

    # Guard all three fields together — the system prompt only expects citations in
    # suggested_response, but checking everything is cheap and avoids a fabricated
    # citation slipping through in a field we didn't anticipate one appearing in.
    allowed_doc_ids = {reference.doc_id.upper() for reference in references}
    combined_text = f"{likely_issue}\n{suggested_next_action}\n{suggested_response}"
    cited_doc_ids = {match.upper() for match in _DOC_ID_PATTERN.findall(combined_text)}
    if cited_doc_ids - allowed_doc_ids:
        return _fallback_draft(references)

    return DraftResult(
        likely_issue=likely_issue,
        suggested_next_action=suggested_next_action,
        suggested_response=suggested_response,
    )


def draft_response(
    ticket: TicketInput,
    category: Category,
    references: list[Reference],
    llm_client: LLMClient,
) -> DraftResult:
    raw_response = llm_client.complete(
        system_prompt=_build_system_prompt(),
        user_prompt=_build_user_prompt(ticket, category, references),
    )
    return _parse_draft_response(raw_response, references)
