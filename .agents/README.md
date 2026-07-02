# Build-Time SDLC Agents

These files define reusable **build-time** AI assistant roles used to help build and manage the Support Ticket Triage Assistant project. They are **not part of the application runtime** — see `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` Section 8 for the build-time-agent-vs-runtime-component distinction.

All roles support the Main Orchestrator and do not independently set conflicting project direction. Most are advisory/document-producing; only the Test/Eval Designer writes code, and only under `tests/`/`evals/`.

- [`product-analyst.md`](product-analyst.md)
- [`solution-architect.md`](solution-architect.md)
- [`implementation-planner.md`](implementation-planner.md)
- [`test-eval-designer.md`](test-eval-designer.md)
- [`code-reviewer.md`](code-reviewer.md)
- [`refactor-reviewer.md`](refactor-reviewer.md)
- [`documentation-agent.md`](documentation-agent.md)
- [`release-manager.md`](release-manager.md)
