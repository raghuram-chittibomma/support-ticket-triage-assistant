# src/

Runtime application code for the Support Ticket Triage Assistant.

This directory is intentionally empty as of the SDLC foundation slice. Application code will be added starting with Slice 1 of the [implementation roadmap](../docs/01_architecture/ARCHITECTURE.md), tracked via GitHub Issues in the `v0.1 SDLC Demo` milestone.

Planned layout (see `docs/01_architecture/ARCHITECTURE.md` for details):

```
src/
  api/            FastAPI app and routes
  ui/             Gradio demo UI
  schemas/        Pydantic models (TicketInput, TriageResult, etc.)
  services/       readiness, missing_info, classifier, priority, response_drafter, confidence, human_review
  retrieval/      knowledge-base retriever
  workflows/      triage pipeline orchestration
  data_access/    file-based loaders for synthetic data
  config.py       application settings
```

Do not place build-time SDLC agent definitions here — those live under `.agents/` at the repo root.
