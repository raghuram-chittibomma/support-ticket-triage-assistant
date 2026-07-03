# Skill: Test/Eval Design

Used by: Test/Eval Designer Agent.

## Checklist

- [ ] Deterministic logic has exact-match unit tests.
- [ ] LLM-backed logic has shape/constraint assertions, not brittle exact-text assertions (see `{{project.docs.test_strategy}}`).
- [ ] New synthetic fixtures added for coverage include realistic phrasing and correct ground truth.
- [ ] Eval scenarios cover major taxonomy/category dimensions at least once.
- [ ] Tests/evals run without requiring network access unless explicitly marked (e.g. `@pytest.mark.llm`).
- [ ] Test files live under `{{project.paths.tests}}`, eval scenario/runner code lives under `{{project.paths.evals}}` — never under `{{project.paths.source}}`.
