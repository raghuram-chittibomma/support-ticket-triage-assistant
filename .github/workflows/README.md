# GitHub Actions workflows

## `ci.yml` — pytest (fast suite)

Runs on every **pull request** and **push** to `main`.

| Step | What it does |
|------|----------------|
| Install | `pip install -e ".[dev]"` from `pyproject.toml` |
| Test | `pytest -m "not llm"` — full suite except the optional LLM smoke test |
| Baseline | Committed `evals/baselines/v0.1.0/fixture-baseline.json` must match a fresh fixture run (see `tests/evals/test_baseline.py`) |

The LLM-marked test (`tests/evals/test_runner.py::test_live_eval_smoke`) is excluded so CI does not need `OPENAI_API_KEY`.

### Require CI on merge

In GitHub **Settings → Branches → Branch protection rules** for `main`, enable **Require status checks to pass** and select **pytest (fast suite)**.
