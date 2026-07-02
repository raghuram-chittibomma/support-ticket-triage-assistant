# Test Strategy — Support Ticket Triage Assistant

## Goals

Give confidence that deterministic logic behaves correctly and predictably, and that the end-to-end pipeline and API produce well-formed, schema-valid output. Tests are the primary quality gate for the deterministic components; evaluation scenarios (see `EVAL_STRATEGY.md`) are the quality gate for LLM-backed behavior.

## Test Levels

- **Unit tests** (`tests/test_*.py`, one file per service): readiness checker, missing-info detector, priority estimator, confidence scorer, human-review decision logic, KB retriever matching logic. Fully deterministic — no network/LLM calls, run fast, run on every PR.
- **Integration tests**: full `triage_pipeline` run against sample tickets in `data/sample/tickets.json`, asserting schema validity of `TriageResult` and correctness of the deterministic fields (category/priority/readiness are checked against `expected_*` fields where the pre-classification rule pass is deterministic enough to assert exactly; LLM-dependent fields are checked for presence/shape, not exact text).
- **API tests**: FastAPI `TestClient` tests for `POST /triage` — request validation, response schema, error handling for malformed input.
- **UI smoke check**: minimal manual or scripted check that the Gradio UI renders and can submit a ticket (full UI automation is out of scope for v0.1).

## What Is and Isn't Asserted Exactly

- Deterministic outputs (readiness, missing fields, priority, human-review flag) are asserted **exactly** against expected values in the synthetic dataset.
- LLM-generated text (classification explanation, drafted response) is asserted for **shape and constraints** (non-empty, references a real `doc_id` if references are present, category matches the expected label) rather than exact wording — exact-wording assertions on LLM output are avoided as brittle.

## Test Data

All tests use the synthetic dataset under `data/sample/` (see `docs/01_architecture/DATA_MODEL.md`). No network calls to third parties are made in unit tests; LLM-backed integration tests either mock the `LLMClient` interface or are marked and run separately (e.g. `@pytest.mark.llm`) so the fast test suite can run without an API key.

## Tooling

pytest, `pytest.mark` for slow/LLM-dependent tests, FastAPI `TestClient` for API tests. CI (GitHub Actions) runs the fast/mocked suite on every PR; LLM-dependent tests may be run manually or in a separate, opt-in CI job if an API key secret is configured.

## Definition of Done Alignment

Every PR that changes runtime behavior must add or update tests covering that behavior, per the repository's Definition of Done (tracked via GitHub Issues, not restated here).
