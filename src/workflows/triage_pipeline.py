"""Triage pipeline orchestration: the single entry point that sequences every deterministic
and LLM-backed service into one `TriageResult`. See docs/01_architecture/ARCHITECTURE.md
'Runtime Workflow' and #22.

Implemented as a plain function (no LangGraph in v0.1, per ADR-001) — see ARCHITECTURE.md
'Extension seams' for how this could be reimplemented as a graph later without changing the
API/service layer's contract.

Sequence (see ARCHITECTURE.md 'Runtime Workflow'): ticket intake/input validation happens via
`TicketInput`'s own Pydantic validation before this function is ever called -> category
classification -> readiness check / missing-information detection -> priority estimation ->
knowledge-base retrieval -> response drafting -> confidence scoring -> human-review decision
-> output formatting (`TriageResult`).
"""

from src.llm import LLMClient, OpenAILLMClient
from src.retrieval import KeywordKBRetriever, Retriever
from src.schemas import TicketInput, TriageResult
from src.services.classifier import classify_ticket
from src.services.confidence import score_confidence
from src.services.human_review import evaluate_human_review
from src.services.priority import estimate_priority
from src.services.readiness import check_readiness
from src.services.response_drafter import draft_response


def run_triage_pipeline(
    ticket: TicketInput,
    llm_client: LLMClient | None = None,
    retriever: Retriever | None = None,
) -> TriageResult:
    """Run the full triage pipeline for a single ticket and return a complete, schema-valid
    `TriageResult`.

    `llm_client`/`retriever` default to the production implementations
    (`OpenAILLMClient`/`KeywordKBRetriever`) but can be swapped — e.g. with a fake in tests,
    or a future provider/vector-store implementation — without touching this function, per
    the `LLMClient`/`Retriever` extension seams documented in `ARCHITECTURE.md`.
    """
    llm_client = llm_client if llm_client is not None else OpenAILLMClient()
    retriever = retriever if retriever is not None else KeywordKBRetriever()

    classification = classify_ticket(ticket, llm_client)
    readiness = check_readiness(ticket, classification.category)
    priority, priority_reason = estimate_priority(ticket)
    references = retriever.retrieve(ticket, classification.category)
    draft = draft_response(ticket, classification.category, references, llm_client)
    confidence_level, _confidence_reason = score_confidence(
        classification.category_confidence, readiness, references
    )
    human_review_required, human_review_reason = evaluate_human_review(
        ticket, priority, confidence_level, readiness
    )

    return TriageResult(
        category=classification.category,
        category_confidence=classification.category_confidence,
        category_explanation=classification.category_explanation,
        priority=priority,
        priority_reason=priority_reason,
        readiness=readiness,
        likely_issue=draft.likely_issue,
        suggested_next_action=draft.suggested_next_action,
        suggested_response=draft.suggested_response,
        references=references,
        confidence_level=confidence_level,
        human_review_required=human_review_required,
        human_review_reason=human_review_reason,
    )
