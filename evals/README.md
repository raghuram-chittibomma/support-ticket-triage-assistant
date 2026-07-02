# evals/

AI evaluation scenarios and the scenario runner for the triage pipeline (classification accuracy, priority accuracy, readiness/missing-info accuracy, response quality spot checks).

Empty as of the SDLC foundation slice. See `docs/02_testing/EVAL_STRATEGY.md` for the evaluation approach. Eval scenarios are built from the same synthetic ticket dataset used for tests (`data/sample/tickets.json`), with `expected_*` ground-truth fields.
