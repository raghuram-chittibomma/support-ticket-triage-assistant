# Evaluation baselines

Pinned snapshots of `python -m evals.run_evals` output for a given release. Used to spot regressions when rules or prompts change.

## Two modes (do not conflate them)

| Mode | Command | API key | What it measures |
|------|---------|---------|------------------|
| **fixture** | `python -m evals.record_baseline --mode fixture --tag v0.1.0` | No | Deterministic dimensions at 100% with `evals/fixture_llm.py` (scripted categories + generic drafts). CI runs this. |
| **live** | `python -m evals.record_baseline --mode live --tag v0.1.0` | Yes | Real OpenAI classification and drafting on all 25 tickets. Run locally at release; commit only if you intend to publish that snapshot. |

Fixture baselines are **not** a substitute for live evals — they prove the runner and deterministic rules against ground truth. Live baselines capture model-dependent accuracy and rubric pass rates.

## Layout

```
evals/baselines/
  QUALITY_BAR.md          acceptance thresholds for v0.1
  v0.1.0/
    fixture-baseline.json
    fixture-baseline.md
    live-baseline.*       optional; add when you run --mode live
```

Ephemeral runs still go to `data/generated/` (gitignored). Only deliberate release snapshots live here.

## Updating a baseline

1. Change code or prompts.
2. Run `pytest -m "not llm"`.
3. Re-run `record_baseline` for the affected mode.
4. If metrics match intent, commit the updated files under the tag folder and note the change in the PR (same as any other test fixture update).

See `docs/02_testing/EVAL_STRATEGY.md` for the overall eval approach.
