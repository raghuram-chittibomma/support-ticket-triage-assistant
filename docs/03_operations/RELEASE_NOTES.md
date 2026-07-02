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

## v0.1 SDLC Demo (planned)

Will include: synthetic product catalog and sample tickets, synthetic knowledge base, ticket schema, deterministic readiness/missing-info/priority/human-review logic, keyword-based retrieval, OpenAI-backed classification and response drafting, FastAPI endpoint, Gradio UI, pytest suite, evaluation scenarios. Entry will be completed and dated when the milestone closes.
