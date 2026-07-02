# Runbook — Support Ticket Triage Assistant

Status: Slice 1 implemented (synthetic data, ticket schema, readiness/missing-info checks). API/UI/LLM-backed pieces land in later slices.

## Local Setup

1. Clone the repository.
2. Create a virtual environment and install dependencies from `pyproject.toml`:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -e ".[dev]"
   ```
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` once `src/config.py` and the classifier/drafter slices land (not required for Slice 1's deterministic services).
4. Synthetic data is already committed under `data/sample/` and `data/knowledge_base/` — no generation step needed (see ADR-002).

## Running the Service (planned)

- API: `uvicorn src.api.main:app --reload` (added in the FastAPI endpoint slice).
- UI: `python -m src.ui.app` or `gradio src/ui/app.py` (added in the Gradio UI slice).

## Running Tests

- `.venv\Scripts\python.exe -m pytest` runs the full deterministic suite (schemas, readiness, missing-info as of Slice 1).
- `pytest -m llm` for LLM-dependent tests, once added (requires `OPENAI_API_KEY`).

## Running Evaluations (planned)

- `python -m evals.run_evals` (added in the evaluation scenario slice) — produces an accuracy report comparing pipeline output to the synthetic ground-truth dataset.

## Regenerating Synthetic Data (planned)

- `python scripts/generate_synthetic_tickets.py` (added in the synthetic data generation slice) — writes output to `data/generated/` (not committed).

## Troubleshooting

- **Missing OpenAI API key:** classification explanation and response drafting will fail; deterministic services (readiness, missing-info, priority) do not require it.
- **Unexpected category/priority results:** check `docs/01_architecture/DATA_MODEL.md` for the rule definitions before assuming a bug in the LLM-backed classifier.
- **`pip install -e ".[dev]"` fails building `pillow` on Python 3.14 (pulled in by `gradio`):** Pillow does not yet ship prebuilt Windows wheels for Python 3.14, and building from source requires zlib headers. This does not block Slice 1 (only `pydantic`/`pydantic-settings`/`pytest`/`httpx` are needed so far). To be resolved before the Gradio UI slice — options: install a Python 3.11–3.13 interpreter for this project's venv, or move to a newer `gradio`/`pillow` release once Windows wheels for 3.14 are published.

## Operational Boundaries

No persistent database in v0.1 — the service is stateless per request. No authentication in v0.1 — do not expose this service on an untrusted network.

This runbook will be filled in with concrete commands as each corresponding GitHub issue/PR lands; keep it in sync with `src/` rather than letting it drift.
