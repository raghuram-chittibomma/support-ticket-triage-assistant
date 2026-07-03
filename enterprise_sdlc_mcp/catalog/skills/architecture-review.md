# Skill: Architecture Review

Used by: Solution Architect Agent, Refactor Reviewer Agent.

## Checklist

- [ ] Change is consistent with `{{project.docs.architecture}}` and existing ADRs, or is accompanied by a new/updated ADR.
- [ ] Deterministic rule/gate logic remains deterministic and explainable — no unnecessary LLM calls introduced into rule logic.
- [ ] LLM usage remains confined to language tasks (classification explanation, drafting, summarization, ambiguity handling).
- [ ] Extension seams ({{project.extensions}}) are respected, not bypassed with direct provider calls scattered through the codebase.
- [ ] No new infrastructure (PostgreSQL, LangGraph, vector DB) is introduced without an ADR justifying it.
- [ ] Complexity is proportional to the project's stated scope.
