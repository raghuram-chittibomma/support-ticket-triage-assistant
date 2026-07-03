# Runbook — Support Ticket Triage Assistant

Status: **v0.1.0 released** (2026-07-03). Slices 1–9 complete: synthetic data and schema, full triage pipeline, FastAPI `/triage`, Gradio UI, evaluation scenario suite, and GitHub Actions CI (`pytest -m "not llm"` on every PR).

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
- UI: `python -m src.ui` (or `python -m src.ui.app`) — opens the Gradio demo at `http://127.0.0.1:7860`. Requires `OPENAI_API_KEY` in the environment/`.env` to actually classify/draft (a missing key surfaces as a clear configuration error in the UI output panel, not a raw traceback).

## Running Tests

- `.venv\Scripts\python.exe -m pytest` runs the full suite, including the classifier, since its unit tests mock `LLMClient` and make no real network calls.
- `pytest -m "not llm"` matches the GitHub Actions CI job (excludes the optional LLM eval smoke test).
- `pytest -m llm` for genuinely LLM-dependent tests (evaluation smoke test hitting the real OpenAI API; requires `OPENAI_API_KEY`).

## UI Smoke Check (Slice 7)

Performed manually during Slice 7 implementation (2026-07-03):

1. `python -m src.ui` — Gradio server started and served `http://127.0.0.1:7860/` (HTTP 200).
2. Form renders subject/body/SKU/persona/channel inputs and a **Triage ticket** button.
3. Submitting a ticket with a valid `OPENAI_API_KEY` set runs the full pipeline and displays all nine result sections (category, priority, readiness, likely issue, next action, draft response, references, confidence, human-review flag) in the output panel.
4. Submitting with an empty subject or body shows a clear inline validation error without calling the pipeline.
5. Submitting without `OPENAI_API_KEY` shows a clear configuration error message in the output panel.

Automated coverage: `tests/ui/test_app.py` exercises the form handler, formatting, and demo construction without launching a browser (full UI automation is out of scope for v0.1, per `TEST_STRATEGY.md`).

- `python -m evals.run_evals` (added in the evaluation scenario slice) — produces an accuracy report comparing pipeline output to the synthetic ground-truth dataset.

## Regenerating Synthetic Data (planned)

- `python scripts/generate_synthetic_tickets.py` (added in the synthetic data generation slice) — writes output to `data/generated/` (not committed).

## Troubleshooting

- **Missing OpenAI API key:** `OpenAILLMClient.complete()` raises `MissingAPIKeyError` with a clear message; the classifier and response drafter need it to run for real. The FastAPI layer converts this to a `500` response; the Gradio UI surfaces it as a configuration error in the output panel. Deterministic services (readiness, missing-info, priority, retrieval, confidence, human-review) do not require it, and the unit test suite never needs it since it mocks `LLMClient`.
- **Unexpected `human_review_required`/`confidence_level` results:** check `docs/01_architecture/DATA_MODEL.md` Sections 12–13 for the exact scoring formula and rule precedence before assuming a bug.
- **`POST /triage` returns a 500 mentioning `OPENAI_API_KEY`:** the server process itself is missing the key (see Local Setup step 3) — this is a deliberate, clear error from a `MissingAPIKeyError` exception handler in `src/api/main.py`, not a bug.
- **`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead` during `pytest`:** a harmless warning from the `fastapi`/`starlette` versions currently pinned; does not affect test correctness. Safe to ignore for v0.1; revisit if/when `httpx2` is adopted upstream.
- **Unexpected category/priority results:** check `docs/01_architecture/DATA_MODEL.md` for the rule definitions before assuming a bug in the LLM-backed classifier.
- **`pip install -e ".[dev]"` fails building `pillow` on Python 3.14 with `gradio>=4,<5`:** Gradio 4.x pins `pillow<11`, which has no prebuilt Windows wheels for Python 3.14. **Resolved in Slice 7:** `pyproject.toml` now pins `gradio>=5,<6`, which pulls in `pillow>=11` with Python 3.14-compatible wheels. If you still hit build failures, use a Python 3.11–3.13 interpreter for this project's venv.

## Operational Boundaries

No persistent database in v0.1 — the service is stateless per request. No authentication in v0.1 — do not expose this service on an untrusted network.

This runbook will be filled in with concrete commands as each corresponding GitHub issue/PR lands; keep it in sync with `src/` rather than letting it drift.
