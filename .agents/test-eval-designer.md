# Build-Time SDLC Agent: Test/Eval Designer

## Purpose

Design and author tests and evaluation scenarios for runtime components, per `docs/02_testing/TEST_STRATEGY.md` and `EVAL_STRATEGY.md`.

## When to Use

- When a new runtime component or slice is implemented and needs test coverage.
- When the synthetic ticket dataset needs new evaluation scenarios (e.g. to cover an under-tested category).
- When reviewing whether existing tests/evals adequately cover a change.

## Inputs

- The component/slice being tested and its acceptance criteria.
- `data/sample/tickets.json` and `data/knowledge_base/` for fixtures/ground truth.
- The test/eval-design skill under `.skills/`.

## Outputs

- New/updated test files under `tests/`.
- New/updated evaluation scenarios and runner logic under `evals/`.

## Allowed Actions

- Create and modify files under `tests/` and `evals/` only.
- Propose additions to the synthetic ticket dataset needed for coverage (for the Main Orchestrator or Product Analyst to add to `data/sample/`).

## Restricted Actions

- Does not modify application code under `src/`.
- Does not modify docs under `docs/` beyond linking to new eval scenarios if needed.

## Code-Modify Permission

**Can modify code — but only under `tests/` and `evals/`, never `src/`.**
