# Release Notes — Support Ticket Triage Assistant

Release facts (tags, published artifacts) live in [GitHub Releases](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/releases). This document is the durable, human-readable log of what shipped in each release and why.

## Unreleased — SDLC Foundation

**Type:** Process/documentation (no application code).

- Established the GitHub-first SDLC operating model: repository, labels, `v0.1 SDLC Demo` milestone, "Support Ticket Triage Assistant" Project board.
- Added durable project docs: `AI_ORCHESTRATOR_BRIEF.md`, `PROJECT_CHARTER.md`, `PRODUCT_BRIEF.md`.
- Added architecture docs: `ARCHITECTURE.md`, `DATA_MODEL.md`, `ADR-001-architecture-choice.md` (Option A — simple pipeline, no PostgreSQL/LangGraph/ChromaDB in v0.1).
- Added `TEST_STRATEGY.md` and `EVAL_STRATEGY.md`.
- Added `AGENTS.md` and build-time SDLC agent/skill definitions under `.agents/` and `.skills/`.
- Created the initial backlog of GitHub issues for the `v0.1 SDLC Demo` milestone.

## Unreleased — Slice 1: Data Foundations, Ticket Schema, Readiness

**Type:** Application code (first slice). PR [#38](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/38), merged 2026-07-02.

- Synthetic data: 8-product NorthPeak Audioworks catalog, 25 sample tickets covering all 13 taxonomy categories, 8 knowledge-base articles (ADR-002 — hand-curated JSON, not generated).
- `src/schemas/`: `TicketInput`, `TriageResult`, `ReadinessResult`, `Reference`, `Category`, `Priority` Pydantic models.
- `src/services/missing_info.py` and `readiness.py`: deterministic, keyword-based per-category readiness checking (documented in `DATA_MODEL.md` Section 4).
- Revised the documented pipeline order: classification now runs before readiness/missing-info detection.
- 74 passing pytest unit tests. Independent Code Reviewer subagent pass: approved with minor suggestions; one finding deferred to a tracked follow-up (#39).

## v0.1 SDLC Demo (in progress)

Will include: the above, plus category classification, priority estimation, keyword-based knowledge retrieval, OpenAI-backed classification explanation and response drafting, confidence scoring, human-review decision logic, FastAPI endpoint, Gradio UI, and evaluation scenarios. Entry will be completed and dated when the milestone closes.
