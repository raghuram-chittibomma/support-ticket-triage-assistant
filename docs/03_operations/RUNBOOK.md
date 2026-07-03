# Runbook — Support Ticket Triage Assistant

Status: Slice 1 (synthetic data, ticket schema, readiness/missing-info checks), Slice 2 (priority estimation, LLM-backed classification), Slice 3 (knowledge-base retrieval, LLM-backed response drafting), Slice 4 (deterministic confidence scoring, human-review decision logic), Slice 5 (full triage pipeline orchestration), and Slice 6 (FastAPI `/triage` endpoint) implemented. The Gradio UI lands in a later slice.

## Running the Pipeline Directly (Python)

```python
from src.schemas import TicketInput
from src.workflows import run_triage_pipeline

ticket = TicketInput(subject="Speaker won't reconnect to Wi-Fi", body="...")
result = run_triage_pipeline(ticket)  # requires OPENAI_API_KEY in the environment
print(result.model_dump_json(indent=2))
```

## Local Setup

1. Clone the repository.
2. Create a virtual environment and install dependencies from `pyproject.toml`:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -e ".[dev]"
   ```
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` if you want to exercise the real classifier or response drafter (`src/services/classifier.py`, `src/services/response_drafter.py`, both via `OpenAILLMClient`). Not required for the deterministic services (readiness, missing-info, priority, retrieval, confidence, human-review) or for the unit test suite, which mocks the `LLMClient` interface.
4. Synthetic data is already committed under `data/sample/` and `data/knowledge_base/` — no generation step needed (see ADR-002).

## Running the Service

- API: `uvicorn src.api.main:app --reload` — then `POST http://127.0.0.1:8000/triage` with a `TicketInput` JSON body, or `GET http://127.0.0.1:8000/health` for a liveness check. Requires `OPENAI_API_KEY` in the environment/`.env` to actually classify/draft (a missing key surfaces as a clear `500` with an `OPENAI_API_KEY` message, not a raw traceback).
- Interactive API docs: `http://127.0.0.1:8000/docs` (FastAPI's auto-generated Swagger UI).
- UI: `python -m src.ui.app` or `gradio src/ui/app.py` (added in the Gradio UI slice, planned).

## Running Tests

- `.venv\Scripts\python.exe -m pytest` runs the full suite, including the classifier, since its unit tests mock `LLMClient` and make no real network calls.
- `pytest -m llm` for genuinely LLM-dependent tests (e.g. evaluation-style tests hitting the real OpenAI API), once added (requires `OPENAI_API_KEY`). No such tests exist yet as of Slice 2.

## Running Evaluations (planned)

- `python -m evals.run_evals` (added in the evaluation scenario slice) — produces an accuracy report comparing pipeline output to the synthetic ground-truth dataset.

## Regenerating Synthetic Data (planned)

- `python scripts/generate_synthetic_tickets.py` (added in the synthetic data generation slice) — writes output to `data/generated/` (not committed).

## Troubleshooting

- **Missing OpenAI API key:** `OpenAILLMClient.complete()` raises a `RuntimeError` with a clear message; the classifier and response drafter need it to run for real. Deterministic services (readiness, missing-info, priority, retrieval, confidence, human-review) do not require it, and the unit test suite never needs it since it mocks `LLMClient`.
- **Unexpected `human_review_required`/`confidence_level` results:** check `docs/01_architecture/DATA_MODEL.md` Sections 12–13 for the exact scoring formula and rule precedence before assuming a bug.
- **`POST /triage` returns a 500 mentioning `OPENAI_API_KEY`:** the server process itself is missing the key (see Local Setup step 3) — this is a deliberate, clear error from a `MissingAPIKeyError` exception handler in `src/api/main.py`, not a bug.
- **`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead` during `pytest`:** a harmless warning from the `fastapi`/`starlette` versions currently pinned; does not affect test correctness. Safe to ignore for v0.1; revisit if/when `httpx2` is adopted upstream.
- **Unexpected category/priority results:** check `docs/01_architecture/DATA_MODEL.md` for the rule definitions before assuming a bug in the LLM-backed classifier.
- **`pip install -e ".[dev]"` fails building `pillow` on Python 3.14 (pulled in by `gradio`):** Pillow does not yet ship prebuilt Windows wheels for Python 3.14, and building from source requires zlib headers. This does not block Slice 1 (only `pydantic`/`pydantic-settings`/`pytest`/`httpx` are needed so far). To be resolved before the Gradio UI slice — options: install a Python 3.11–3.13 interpreter for this project's venv, or move to a newer `gradio`/`pillow` release once Windows wheels for 3.14 are published.

## Operational Boundaries

No persistent database in v0.1 — the service is stateless per request. No authentication in v0.1 — do not expose this service on an untrusted network.

This runbook will be filled in with concrete commands as each corresponding GitHub issue/PR lands; keep it in sync with `src/` rather than letting it drift.
