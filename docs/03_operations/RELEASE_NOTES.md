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
- `src/services/missing_info.py` and `readiness.py`: deterministic, keyword-based per-category readiness checking (documented in `DATA_MODEL.md` Section 5 — renumbered from Section 4 in Slice 2 to make room for the new Priority Rule Keyword Detail section).
- Revised the documented pipeline order: classification now runs before readiness/missing-info detection.
- 74 passing pytest unit tests. Independent Code Reviewer subagent pass: approved with minor suggestions; one finding deferred to a tracked follow-up (#39).

## Unreleased — Slice 2: Priority Estimation, LLM-Backed Classification

**Type:** Application code. PR [#40](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/40), merged 2026-07-02.

- `src/services/priority.py`: deterministic, ordered keyword rule list (Urgent > High > Low(informational/cosmetic) > Medium default) — documented in `DATA_MODEL.md` Section 4. No LLM call.
- `src/config.py`: `pydantic-settings` `Settings` for `OPENAI_API_KEY` / `OPENAI_MODEL`, loaded from `.env` (see `.env.example`).
- `src/llm/client.py`: the `LLMClient` extension seam (Protocol) plus the default `OpenAILLMClient` implementation, constructed lazily so no API key is required at import time.
- `src/services/classifier.py`: deterministic keyword/product-hint pre-filter (`rank_categories`) plus an `LLMClient` call for final category confirmation and explanation; `category_confidence` is a deterministic function of pre-filter/LLM agreement.
- Unit tests mock `LLMClient` throughout (a `FakeLLMClient`) — no network calls in the fast test suite, per `TEST_STRATEGY.md`. Real classification accuracy is deferred to the evaluation scenario suite (#26), not asserted in unit tests.
- All 25 sample tickets' `expected_priority` values verified against the new deterministic rules with no dataset changes needed.
- Independent Code Reviewer subagent pass: requested changes on one blocking bug (short keywords like "shock"/"dent" false-positived via plain substring matching, e.g. "shockproof" incorrectly triggering the Urgent safety rule); fixed with word-boundary matching plus regression tests. One unrelated, pre-existing stale doc reference found during review deferred to a tracked follow-up (#41). 127 passing pytest unit tests after fixes.
- Story #33 (priority) closed — its Definition of Done is fully met. Story #32 (classification) stays open/in-progress — its Definition of Done additionally requires measuring classification accuracy via the evaluation scenario suite (#26), not yet built.

## Unreleased — Slice 3: Knowledge Retrieval, LLM-Backed Response Drafting

**Type:** Application code. PR [#42](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/42), merged 2026-07-02.

- `src/retrieval/kb_retriever.py`: `Retriever` extension seam (Protocol) plus `KeywordKBRetriever` — filters `data/knowledge_base/` articles by `category_tags` matching the classified category (the primary relevance signal; categories with no KB coverage correctly return zero references), then ranks same-category candidates by deterministic keyword-overlap + product-tag scoring. No vector database in v0.1.
- `src/services/response_drafter.py`: an `LLMClient` call that drafts a customer response grounded in retrieved references. A deterministic post-generation check falls back to a safe templated response if the model cites a `doc_id` that wasn't actually retrieved — a citation can never be fabricated even if the model ignores its system prompt instructions.
- Unit tests mock `LLMClient` throughout; no network calls in the fast test suite. Response quality is deferred to the evaluation scenario suite (#26), per `EVAL_STRATEGY.md`.
- Independent Code Reviewer subagent pass: retrieval layer (#18) approved with no findings; response drafter (#19) requested changes on one blocking bug — the fabrication guard had case-sensitivity and numeric-suffix-shape bypasses letting a fabricated citation slip through undetected (including with zero retrieved references). Fixed with a looser, case-insensitive doc_id pattern plus regression tests. 173 passing pytest unit tests after fixes.
- Story #34 (retrieval) closed — its Definition of Done is fully met. Story #35 (response drafting) stays open/in-progress — its Definition of Done additionally requires applying the response-quality rubric via the evaluation scenario suite (#26), not yet built.

## Unreleased — Slice 4: Confidence Scoring, Human-Review Decision Logic

**Type:** Application code. PR TBD.

- `src/services/confidence.py`: deterministic combination of classifier `category_confidence`, readiness, and retrieval match strength into `confidence_level` (high/medium/low) — resolves the confidence-weighting open question from `AI_ORCHESTRATOR_BRIEF.md` Section 16 (documented in `DATA_MODEL.md` Section 12). No LLM call.
- `src/services/human_review.py`: deterministic, ordered rule list — Urgent priority or escalation language always flag review; otherwise low confidence, or medium confidence combined with an incomplete ticket, flags review (documented in `DATA_MODEL.md` Section 13). No LLM call. Reuses `priority.py`'s `ESCALATION_KEYWORDS` (via a new `detect_escalation_language` helper) rather than duplicating the list.
- Both services take already-computed upstream signals as plain arguments (no LLM/network dependency), so unit tests need no mocking.

## v0.1 SDLC Demo (in progress)

Will include: the above, plus FastAPI endpoint, Gradio UI, pipeline orchestration, and evaluation scenarios. Entry will be completed and dated when the milestone closes.
