"""FastAPI service exposing the triage pipeline over HTTP. See
docs/01_architecture/ARCHITECTURE.md 'API/service layer' and #23.

The `POST /triage` path operation is declared as a plain `def` (not `async def`).
`run_triage_pipeline` makes blocking HTTP calls internally (via `OpenAILLMClient`, which
uses the synchronous `openai` SDK), and FastAPI automatically runs synchronous path
operation functions in an external threadpool rather than calling them directly on the
event loop — this is the documented, idiomatic way to host a blocking call without extra
async plumbing. See .skills/fastapi-service-review.md ("No blocking/long-running calls ...
without appropriate async handling").
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.schemas import TicketInput, TriageResult
from src.workflows import run_triage_pipeline

app = FastAPI(
    title="Support Ticket Triage Assistant",
    description="AI-assisted support ticket triage demo for the fictional NorthPeak Audioworks.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResult)
def triage(ticket: TicketInput) -> TriageResult:
    """Run the full triage pipeline for a single ticket and return a complete TriageResult.

    `ticket` is validated against `TicketInput` automatically by FastAPI/Pydantic before
    this function is ever called — a malformed request body (missing/empty required
    fields, wrong types, invalid `channel` value, etc.) short-circuits to a 422 response
    without reaching pipeline code. Configuration (OpenAI key, model) comes from
    `src/config.py` via the default `LLMClient`/`Retriever` constructed inside
    `run_triage_pipeline()` — never hardcoded here.
    """
    return run_triage_pipeline(ticket)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
    # In practice this is OpenAILLMClient's "OPENAI_API_KEY is not set" error — a server
    # configuration problem, not a malformed request — surfaced as a clear 500 with the
    # actual message rather than an unhandled-exception traceback.
    return JSONResponse(status_code=500, content={"detail": str(exc)})
