# Architecture — Support Ticket Triage Assistant

Status: v0.1 (Option A — Simple architecture). See `docs/01_architecture/DECISIONS/ADR-001-architecture-choice.md` for the decision record and alternative considered.

## Architecture Diagram

```mermaid
flowchart TD
    UI["Gradio UI (src/ui)"] --> API["FastAPI service (src/api)"]
    API --> Pipeline["Triage Pipeline (src/workflows/triage_pipeline.py)"]
    Pipeline --> Classifier["Ticket Classifier"]
    Pipeline --> Readiness["Readiness Checker"]
    Pipeline --> MissingInfo["Missing-Info Detector"]
    Pipeline --> Priority["Priority Estimator"]
    Pipeline --> Retriever["KB Retriever"]
    Pipeline --> Drafter["Response Drafter"]
    Pipeline --> Confidence["Confidence Scorer"]
    Pipeline --> HumanReview["Human-Review Decision"]
    Classifier --> LLM["OpenAI LLM Client"]
    Drafter --> LLM
    Retriever --> KB["Synthetic Knowledge Base (data/knowledge_base)"]
    Pipeline --> DataAccess["Data Access (products/tickets)"]
    DataAccess --> SyntheticData["Synthetic Data (data/sample)"]
```

## Layers

- **UI layer** (`src/ui/`): Gradio app for manual demo use; calls the API layer (or the pipeline directly in-process for the simplest v0.1 wiring).
- **API/service layer** (`src/api/`): FastAPI app exposing `POST /triage`, request/response validated via Pydantic schemas.
- **Schemas** (`src/schemas/`): `TicketInput`, `TriageResult`, `Category`, `Priority`, `ReadinessResult`, `Reference`.
- **Ticket classifier** (`src/services/classifier.py`): keyword/rule pre-filter plus an OpenAI call for category confirmation and a human-readable explanation. Runs before readiness/missing-info detection (see Runtime Workflow note below).
- **Ticket readiness checker** (`src/services/readiness.py`): deterministic — does the ticket contain enough information to triage confidently for its classified category?
- **Missing information detector** (`src/services/missing_info.py`): deterministic, per-category required-field rules (e.g. Wi-Fi issues need product model + network type + firmware version).
- **Priority estimator** (`src/services/priority.py`): deterministic rules based on safety keywords, functional impact, urgency language, and time sensitivity.
- **Knowledge retrieval layer** (`src/retrieval/kb_retriever.py`): keyword/tag-based matching over the synthetic knowledge base (no vector database in v0.1).
- **Response drafting layer** (`src/services/response_drafter.py`): OpenAI call that drafts a customer response grounded in retrieved references.
- **Confidence scoring** (`src/services/confidence.py`): deterministic combination of classifier confidence, readiness, and retrieval match strength.
- **Human-review decision logic** (`src/services/human_review.py`): deterministic threshold and escalation-keyword gate.
- **Evaluation layer** (`evals/`): scenario runner comparing pipeline output to expected ground truth in the synthetic ticket dataset.
- **Test layer** (`tests/`): pytest unit tests per service plus integration tests for the pipeline and API.
- **Configuration layer** (`src/config.py`): pydantic-settings for the OpenAI key, data file paths, and rule thresholds.
- **PostgreSQL layer**: not present in v0.1 (see ADR-001 and the Data Model doc for the reserved forward-looking schema).

## Extension seams (for v0.2+, not built in v0.1)

To avoid a rewrite later, v0.1 code is written behind small interfaces:

- `LLMClient` — wraps the OpenAI call; a future provider can implement the same interface.
- `Retriever` — wraps keyword retrieval; a future `ChromaRetriever` can implement the same interface for semantic search.
- `TriageRepository` — not implemented in v0.1; a future PostgreSQL-backed implementation can persist tickets/results/audit trail without changing the pipeline's calling code.
- `triage_pipeline.py` is a plain function/class today; if the workflow gains branching or looping (e.g. iterative clarification), it can be reimplemented as a LangGraph graph without changing the service/API layer's contract.

## Runtime Workflow

See `docs/01_architecture/DATA_MODEL.md` for schemas and `docs/00_project/PRODUCT_BRIEF.md` for functional requirements. Workflow sequence:

Ticket intake → input validation → category classification → readiness check → missing-information detection → priority estimation → knowledge-base retrieval (if applicable) → response drafting → confidence scoring → human-review decision → output formatting.

**Note (revised during Slice 1 implementation of #14/#15):** classification runs *before* readiness/missing-information detection, not after as originally sketched — the per-category required-field rules in `DATA_MODEL.md` Section 4 need to know the category to know which fields to check for. `readiness.py` and `missing_info.py` both take the classified `Category` as an explicit parameter alongside the `TicketInput`, keeping them deterministic, unit-testable in isolation, and unaware of how the category was produced.

No persistence step occurs in v0.1; a persistence extension point is documented but unimplemented.
