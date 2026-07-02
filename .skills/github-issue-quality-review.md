# Skill: GitHub Issue Quality Review

Used by: Product Analyst Agent, Implementation Planner Agent, Main Orchestrator.

## Checklist

- [ ] Meets the repository's Definition of Ready (see `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` / repository-level Definition of Ready).
- [ ] Acceptance criteria are verifiable by a test or eval, not just prose.
- [ ] Labels are complete and consistent with the taxonomy (work type, phase, priority, component/agent, status flags).
- [ ] Dependencies are explicit and linked, and are not circular.
- [ ] No scope creep beyond what the title promises.
- [ ] Runtime-component issues do not reference build-time agent roles as if they were application code, and vice versa.
- [ ] Every technical task issue is linked as a GitHub sub-issue under a `type:story` or `type:epic` parent - no orphaned tasks that trace to nothing but an architecture component (see `.skills/github-backlog-creation.md`).
- [ ] Story issues have a persona-based narrative and Given/When/Then acceptance criteria written in user-observable terms, not implementation/schema details.
