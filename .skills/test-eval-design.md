# Skill: Test/Eval Design

Used by: Test/Eval Designer Agent.

## Checklist

- [ ] Deterministic logic has exact-match unit tests (readiness, missing-info, priority, confidence, human-review).
- [ ] LLM-backed logic has shape/constraint assertions, not brittle exact-text assertions (see `docs/02_testing/TEST_STRATEGY.md`).
- [ ] New synthetic tickets added for coverage include realistic phrasing and correct `expected_*` ground truth.
- [ ] Eval scenarios cover every category in the taxonomy at least once.
- [ ] Tests/evals run without requiring network access unless explicitly marked (e.g. `@pytest.mark.llm`).
- [ ] Test file lives under `tests/`, eval scenario/runner code lives under `evals/` — never under `src/`.
