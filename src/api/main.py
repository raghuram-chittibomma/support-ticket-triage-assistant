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

from src.llm import MissingAPIKeyError
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
    without reaching pipeline code.     Configuration (OpenAI key, model) comes from `src/config.py` via the default
    `LLMClient`/`Retriever` constructed inside `run_triage_pipeline()` — never hardcoded
    here. A missing API key surfaces as a `MissingAPIKeyError`, handled below.
    """
    return run_triage_pipeline(ticket)


@app.exception_handler(MissingAPIKeyError)
async def missing_api_key_error_handler(request: Request, exc: MissingAPIKeyError) -> JSONResponse:
    # Scoped to this specific configuration-error subclass (not a bare RuntimeError) so an
    # unrelated bug elsewhere in the pipeline can't be silently masked as "missing API key"
    # — see the independent Code Reviewer subagent finding on PR #45.
    return JSONResponse(status_code=500, content={"detail": str(exc)})
