# Skill: LangGraph Workflow Review

Used by: Solution Architect Agent. Applies only if/when LangGraph is adopted (not used in v0.1 — see ADR-001).

## Checklist

- [ ] A concrete branching/looping requirement (not speculative) justifies LangGraph — documented in an ADR.
- [ ] Each graph node maps to an existing runtime component (readiness, classifier, priority, retriever, drafter, confidence, human-review) rather than introducing parallel, duplicate logic.
- [ ] The API/service layer's external contract (`POST /triage` request/response schema) is unchanged by the internal orchestration swap.
- [ ] Graph state is explicit and typed (Pydantic), not implicit dict-passing.
- [ ] Tests cover graph edges/branches, not just the happy path.
