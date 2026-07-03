---
name: Eval regression
about: Live or fixture eval run missed the quality bar or introduced unexpected mismatches
title: "Eval regression: "
labels: type:bug
---

## Run details

- **Mode:** fixture / live
- **Tag or branch:**
- **Command:** `python -m evals.record_baseline --mode …`
- **Recorded at:** <!-- ISO timestamp from report header -->

## Summary metrics

| Dimension | Expected (see QUALITY_BAR.md) | Actual |
|-----------|-------------------------------|--------|
| Category accuracy | | |
| Priority accuracy | | |
| Missing-fields accuracy | | |
| Rubric pass rate | | |

## Mismatches

<!-- Paste ticket IDs and fields from the report, or attach evals/baselines/.../fixture-baseline.md -->

## Likely cause

<!-- Rule change, prompt change, dataset drift, model behavior — your best guess -->

## Proposed fix

- [ ] Code / prompt fix
- [ ] Update baseline (if intentional behavior change)
- [ ] Update QUALITY_BAR.md (only with explicit rationale)
