# Runbook — Support Ticket Triage Assistant

Status: skeleton, to be filled in as `src/` is implemented (tracked via GitHub issues in later slices).

## Local Setup (planned)

1. Clone the repository.
2. Create a Python virtual environment and install dependencies (`requirements.txt` / `pyproject.toml` — added in the implementation slices).
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (added alongside `src/config.py`).
4. Generate or use committed synthetic data under `data/sample/` and `data/knowledge_base/`.

## Running the Service (planned)

- API: `uvicorn src.api.main:app --reload` (added in the FastAPI endpoint slice).
- UI: `python -m src.ui.app` or `gradio src/ui/app.py` (added in the Gradio UI slice).

## Running Tests (planned)

- `pytest` for the fast/deterministic suite.
- `pytest -m llm` for LLM-dependent tests (requires `OPENAI_API_KEY`).

## Running Evaluations (planned)

- `python -m evals.run_evals` (added in the evaluation scenario slice) — produces an accuracy report comparing pipeline output to the synthetic ground-truth dataset.

## Regenerating Synthetic Data (planned)

- `python scripts/generate_synthetic_tickets.py` (added in the synthetic data generation slice) — writes output to `data/generated/` (not committed).

## Troubleshooting

- **Missing OpenAI API key:** classification explanation and response drafting will fail; deterministic services (readiness, missing-info, priority) do not require it.
- **Unexpected category/priority results:** check `docs/01_architecture/DATA_MODEL.md` for the rule definitions before assuming a bug in the LLM-backed classifier.

## Operational Boundaries

No persistent database in v0.1 — the service is stateless per request. No authentication in v0.1 — do not expose this service on an untrusted network.

This runbook will be filled in with concrete commands as each corresponding GitHub issue/PR lands; keep it in sync with `src/` rather than letting it drift.
