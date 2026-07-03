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
  api/            FastAPI app: POST /triage, GET /health (#23, Slice 6)
  ui/             Gradio demo UI (#24, Slice 7) — calls run_triage_pipeline in-process
```

Still planned (see `docs/01_architecture/ARCHITECTURE.md`):

```
src/
  (none — runtime application code complete for v0.1 demo; evals/ and CI remain)
```

Do not place build-time SDLC agent definitions here — those live under `.agents/` at the repo root.
