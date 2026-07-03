# src/

Runtime application code for the Support Ticket Triage Assistant.

Implemented so far:

```
src/
  schemas/        TicketInput, TriageResult, ReadinessResult, Reference, Category, Priority (Slice 1, #13)
  services/       readiness.py (#14), missing_info.py (#15), priority.py (#17), classifier.py (#16),
                  response_drafter.py (#19, Slice 3), confidence.py (#20), human_review.py (#21, Slice 4)
  data_access/    file-based loaders for data/sample and data/knowledge_base (Slice 1)
  llm/            LLMClient Protocol + OpenAILLMClient (Slice 2)
  config.py       pydantic-settings Settings (OPENAI_API_KEY, OPENAI_MODEL) (Slice 2)
  retrieval/      KeywordKBRetriever (#18, Slice 3)
```

Still planned (see `docs/01_architecture/ARCHITECTURE.md`):

```
src/
  api/            FastAPI app and routes
  ui/             Gradio demo UI
  workflows/      triage pipeline orchestration
```

Do not place build-time SDLC agent definitions here — those live under `.agents/` at the repo root.
