# src/

Runtime application code for the Support Ticket Triage Assistant.

Implemented so far (Slice 1, issues #13-#15):

```
src/
  schemas/        TicketInput, TriageResult, ReadinessResult, Reference, Category, Priority
  services/       readiness.py (#14), missing_info.py (#15)
  data_access/    file-based loaders for data/sample and data/knowledge_base
```

Still planned (see `docs/01_architecture/ARCHITECTURE.md`):

```
src/
  api/            FastAPI app and routes
  ui/             Gradio demo UI
  services/       classifier, priority, response_drafter, confidence, human_review
  retrieval/      knowledge-base retriever
  workflows/      triage pipeline orchestration
  config.py       application settings
```

Do not place build-time SDLC agent definitions here — those live under `.agents/` at the repo root.
