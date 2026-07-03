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

**Type:** Application code. PR [#43](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/43), merged 2026-07-02.

- `src/services/confidence.py`: deterministic combination of classifier `category_confidence`, readiness, and retrieval match strength into `confidence_level` (high/medium/low) — resolves the confidence-weighting open question from `AI_ORCHESTRATOR_BRIEF.md` Section 16 (documented in `DATA_MODEL.md` Section 12). No LLM call.
- `src/services/human_review.py`: deterministic, ordered rule list — Urgent priority or escalation language always flag review; otherwise low confidence, or medium confidence combined with an incomplete ticket, flags review (documented in `DATA_MODEL.md` Section 13). No LLM call. Reuses `priority.py`'s `ESCALATION_KEYWORDS` (via a new `detect_escalation_language` helper) rather than duplicating the list.
- Both services take already-computed upstream signals as plain arguments (no LLM/network dependency), so unit tests need no mocking.
- Independent Code Reviewer subagent pass: requested changes on one blocking bug — IEEE-754 float drift (e.g. `0.7 - 0.25 + 0.05 == 0.49999999999999994`) could push a score mathematically exactly at the documented `0.5`/`0.75` threshold into the bucket below it, with the printed reason string contradicting the returned level. Fixed by rounding the clamped score to 2 decimals before thresholding, plus boundary regression tests and an added Urgent-vs-low-confidence precedence test. 195 passing pytest unit tests after fixes.
- Story #36 (confidence/human-review) closed — its Definition of Done is fully met (both sub-issues closed, unit-tested per level and per flagged/non-flagged case).

## Unreleased — Slice 5: Triage Pipeline Orchestration

**Type:** Application code. PR [#44](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/44), merged 2026-07-02.

- `src/workflows/triage_pipeline.py`: `run_triage_pipeline()`, the single entry point sequencing every Slice 1-4 service into one schema-valid `TriageResult` — classification → readiness/missing-info → priority → retrieval → drafting → confidence → human-review → output formatting (`DATA_MODEL.md` Section 15). A plain function, per ADR-001 (no LangGraph in v0.1); `llm_client`/`retriever` are injectable for testing.
- `src/services/response_drafter.py` extended: now produces a structured `DraftResult` (`likely_issue`, `suggested_next_action`, `suggested_response`) from a single LLM call, filling a gap where those first two fields had no dedicated backlog item of their own (`DATA_MODEL.md` Section 14). The citation-fabrication guard now covers all three fields.
- Extracted `strip_markdown_code_fence` (previously private/duplicated logic in `classifier.py`) to a shared `src/llm/utils.py` helper, now reused by both LLM-backed services.
- Integration tests (`tests/workflows/test_triage_pipeline.py`) run the full pipeline against all 25 `data/sample/tickets.json` fixtures with a scripted `LLMClient`, asserting deterministic fields (category, priority, readiness) exactly and LLM-backed fields for shape/presence only, per #22's acceptance criteria.
- Independent Code Reviewer subagent pass: approved with minor, non-blocking suggestions (a `str(None)` → literal `"None"` edge case in the draft-parsing null handling, a couple of under-specified test assertions, missing direct unit tests for the new `strip_markdown_code_fence` helper). All addressed with fixes and new regression tests. 234 passing pytest unit/integration tests after fixes.

## Unreleased — Slice 6: FastAPI `/triage` Endpoint

**Type:** Application code. PR [#45](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/45), merged 2026-07-03.

- `src/api/main.py`: `POST /triage` (request/response validated via `TicketInput`/`TriageResult`) and `GET /health`. The path operation is a plain `def`, letting FastAPI run the pipeline's blocking LLM calls in its external threadpool automatically rather than on the event loop, per `.skills/fastapi-service-review.md`.
- A dedicated `MissingAPIKeyError` (`src/llm/client.py`, a `RuntimeError` subclass) exception handler converts `OpenAILLMClient`'s missing-API-key error into a clear `500` response instead of an unhandled-exception traceback.
- Malformed requests (missing/empty required fields, invalid `channel`, non-JSON body) never reach pipeline code — FastAPI/Pydantic short-circuits to a `422` first.
- Integration tests (`tests/api/test_main.py`) use FastAPI's `TestClient`, faking the LLM by patching `OpenAILLMClient` where `run_triage_pipeline` looks it up — no real network calls.
- Manually smoke-tested with a real `uvicorn` process: `/health` and `/triage`'s validation-error path both confirmed working end-to-end.
- Independent Code Reviewer subagent pass: approved with no blocking bugs. The reviewer independently verified the async/blocking-threadpool claim against the actually-installed `starlette` version and probed the running app with edge-case payloads. Non-blocking suggestion adopted: scoped the missing-API-key exception handler to a dedicated `MissingAPIKeyError` type rather than a bare `RuntimeError`, so an unrelated future bug can't be silently masked as a "missing key" problem. 246 passing pytest unit/integration tests after fixes.

## Unreleased — Slice 7: Gradio Demo UI

**Type:** Application code. PR [#46](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/46), merged 2026-07-03.

- `src/ui/app.py`: Gradio demo UI — paste a ticket (subject, body, optional SKU/persona/channel) and view the full triage result in one screen. **v0.1 wiring choice:** calls `run_triage_pipeline()` in-process rather than the FastAPI `/triage` endpoint, so the demo runs with a single `python -m src.ui` command (documented in `ARCHITECTURE.md`).
- `src/ui/formatting.py`: renders a `TriageResult` as readable Markdown covering all nine Story #37 result fields.
- `pyproject.toml`: bumped `gradio` pin from `>=4.36,<5` to `>=5,<6` — Gradio 5 pulls in `pillow>=11` with Python 3.14-compatible Windows wheels, resolving the long-standing Pillow build failure noted in `RUNBOOK.md`.
- Manual smoke check performed and documented in `RUNBOOK.md` (UI Smoke Check section).
- `tests/ui/test_app.py`: tests form validation, formatting, error handling, and demo construction without browser automation.
- Independent Code Reviewer subagent pass: approved with no blocking bugs; adopted suggestions for a generic unexpected-error handler in the UI, a ValidationError unit test, and corrected stale `MissingAPIKeyError` wording in `RUNBOOK.md`. 257 passing pytest unit/integration tests after fixes.

## Unreleased — Slice 8: Evaluation Scenario Suite

**Type:** Test/eval infrastructure. PR [#52](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/52), merged 2026-07-03.

- `evals/`: scenario loader, runner, response-quality rubric (`evals/RUBRIC.md`), JSON/Markdown report writer, and `python -m evals.run_evals` CLI.
- Loads all 25 tickets from `data/sample/tickets.json`, runs the full pipeline, compares `expected_*` ground truth, and applies a heuristic response rubric to every draft.
- `@pytest.mark.llm` smoke test for optional live OpenAI runs; fast CI suite excludes it via `pytest -m "not llm"`.
- Independent Code Reviewer subagent pass (Bugbot): approved with no bugs. 271 passing pytest tests after merge.

## Unreleased — Slice 9: GitHub Actions CI

**Type:** Delivery infrastructure. PR [#54](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/54), merged 2026-07-03.

- `.github/workflows/ci.yml`: runs `pytest -m "not llm"` on every PR and push to `main` (Python 3.12, Ubuntu).
- `.github/workflows/README.md`: documents the workflow and branch-protection setup.
- Independent Code Reviewer via Enterprise SDLC MCP: approved; CI check **pytest (fast suite)** passed on the PR.

## Unreleased — Enterprise SDLC MCP v1 (separate program)

**Type:** Build-time tooling (not runtime product). PR [#51](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/51), merged 2026-07-03. Tracked under `program:enterprise-sdlc`, not the triage product milestone deliverables.

- `enterprise_sdlc_mcp/`: MCP server exposing 8 parameterized agent roles and 13 generic SDLC skills.
- `sdlc.project.yaml`, `.cursor/mcp.json`, and MCP-first pre-merge review guidance (`AGENTS.md`, `.cursor/rules/enterprise-sdlc-pr-review.mdc`).

## v0.1.0 — SDLC Demo

**Released:** 2026-07-03. **Tag:** `v0.1.0`. **Milestone:** v0.1 SDLC Demo.

### Summary

First complete release of the NorthPeak Audioworks support-ticket triage assistant demo and the GitHub-first SDLC case study that built it.

**Runtime product:** End-to-end triage pipeline (classification, readiness, priority, KB retrieval, response drafting, confidence, human-review) exposed via FastAPI (`POST /triage`) and a Gradio demo UI. All data synthetic; deterministic rules for gates/scoring; LLM for classification explanation and response drafting only.

**Quality gates:** 271-test pytest suite (fast/mocked by default), evaluation scenario runner with response rubric, GitHub Actions CI on every PR.

**Delivery model:** Story → task GitHub backlog, thin vertical slices, independent Code Reviewer before merge (Enterprise SDLC MCP from Slice 9 onward).

### Deferred post-v0.1.0

- **#39** — Harden missing-info keyword rules against realistic phrasing (P2; tracked follow-up from Slice 1 review).
- **#41** — Stale doc reference in PostgreSQL schema review skill (P3; enterprise MCP catalog path).

### How to run

See `docs/03_operations/RUNBOOK.md`. Quick start: `python -m src.ui` (UI) or `uvicorn src.api.main:app` (API). Requires `OPENAI_API_KEY` for live classification/drafting.
