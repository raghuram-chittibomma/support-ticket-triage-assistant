# evals/

AI evaluation scenarios and the scenario runner for the triage pipeline.

## Run manually (requires `OPENAI_API_KEY`)

```powershell
.\.venv\Scripts\python.exe -m evals.run_evals
```

Optional flags:

- `--limit 5` — quick run on first N tickets
- `--output data/generated/my-eval` — custom report base name (writes `.json` and `.md`)

Reports are written under `data/generated/` (gitignored).

## Rubric

See [`RUBRIC.md`](RUBRIC.md) for the response-quality checks applied to every drafted response.

## Strategy

See `docs/02_testing/EVAL_STRATEGY.md`. Scenarios load ground truth from `data/sample/tickets.json` (`expected_category`, `expected_priority`, `expected_missing_fields`).
