# src/

Runtime application code for the Support Ticket Triage Assistant.

Implemented so far:

```
src/
  schemas/        TicketInput, TriageResult, ReadinessResult, Reference, Category, Priority (Slice 1, #13)
  services/       readiness.py (#14), missing_info.py (#15), priority.py (#17), classifier.py (#16),
                  response_drafter.py (#19, Slice 3; extended Slice 5 to also produce likely_issue/
                  suggested_next_action), confidence.py (#20), human_review.py (#21, Slice 4)
  data_access/    file-based loaders for data/sample and data/knowledge_base (Slice 1)
  llm/            LLMClient Protocol + OpenAILLMClient (Slice 2); utils.py shared JSON-parsing helper (Slice 5)
  config.py       pydantic-settings Settings (OPENAI_API_KEY, OPENAI_MODEL) (Slice 2)
  retrieval/      KeywordKBRetriever (#18, Slice 3)
  workflows/      run_triage_pipeline (#22, Slice 5) — single entry point sequencing every service above
```

Still planned (see `docs/01_architecture/ARCHITECTURE.md`):

```
src/
  api/            FastAPI app and routes
  ui/             Gradio demo UI
```

Do not place build-time SDLC agent definitions here — those live under `.agents/` at the repo root.
