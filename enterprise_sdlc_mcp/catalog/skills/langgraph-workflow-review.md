# Skill: LangGraph Workflow Review

Used by: Solution Architect Agent. Applies only if/when LangGraph is adopted.

## Checklist

- [ ] A concrete branching/looping requirement (not speculative) justifies LangGraph — documented in an ADR.
- [ ] Each graph node maps to an existing runtime component rather than introducing parallel, duplicate logic.
- [ ] The API/service layer's external contract is unchanged by the internal orchestration swap.
- [ ] Graph state is explicit and typed (e.g. Pydantic), not implicit dict-passing.
- [ ] Tests cover graph edges/branches, not just the happy path.
