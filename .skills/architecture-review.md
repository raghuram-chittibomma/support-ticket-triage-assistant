# Skill: Architecture Review

Used by: Solution Architect Agent, Refactor Reviewer Agent.

## Checklist

- [ ] Change is consistent with `docs/01_architecture/ARCHITECTURE.md` and existing ADRs, or is accompanied by a new/updated ADR.
- [ ] Deterministic logic (readiness, missing-info, priority, human-review) remains deterministic and explainable — no unnecessary LLM calls introduced into rule/gate logic.
- [ ] LLM usage remains confined to classification explanation, response drafting, summarization, and ambiguity handling.
- [ ] Extension seams (`LLMClient`, `Retriever`, `TriageRepository`) are respected, not bypassed with direct provider calls scattered through the codebase.
- [ ] No new infrastructure (PostgreSQL, LangGraph, ChromaDB) is introduced without an ADR justifying it.
- [ ] Complexity is proportional to the single-user portfolio/demo scope.
