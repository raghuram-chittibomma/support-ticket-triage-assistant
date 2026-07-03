# v0.1 quality bar

Acceptance thresholds for the **live** evaluation run (`--mode live`). Fixture baselines in CI enforce deterministic dimensions only.

| Dimension | Bar (v0.1) | Rationale |
|-----------|------------|-----------|
| Priority accuracy | 100% | Pure keyword rules; any miss is a bug (#40). |
| Missing-fields accuracy | ≥ 96% | Keyword readiness rules; known gaps tracked in #39. |
| Category accuracy (live LLM) | ≥ 80% | Primary signal for story #32; not asserted in unit tests. |
| Response rubric check pass rate (live) | ≥ 90% | Heuristic spot-check for story #35; human review remains backstop. |

**CI gate:** `pytest -m "not llm"` plus fixture baseline summary match (see `.github/workflows/ci.yml`).

**Not a CI gate in v0.1:** live eval (requires `OPENAI_API_KEY`, non-deterministic). Record manually at release and compare to this bar before tagging.

If a live run misses a bar, open an eval-regression issue (template: `.github/ISSUE_TEMPLATE/eval_regression.md`) rather than lowering the threshold without discussion.
