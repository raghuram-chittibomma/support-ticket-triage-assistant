# Skill: GitHub Backlog Creation

Used by: Implementation Planner Agent (primarily), Main Orchestrator.

## Story-Task Hierarchy (required)

Do not create flat, architecture-shaped task lists. Every piece of user-facing work must trace to a **user story** before it becomes technical **tasks**:

1. Identify the functional requirement (FR) in `docs/00_project/PRODUCT_BRIEF.md` the work serves.
2. If no story issue exists for that FR yet, create one first: title `Story: <capability> (FR<n>)`, labeled `type:story`, with a persona-based "As a / I want / so that" narrative and Given/When/Then acceptance criteria written in user-observable terms (no schema/interface details).
3. Create the technical task issue(s) as usual, then link each as a **GitHub sub-issue** of the story (`gh api repos/{owner}/{repo}/issues/{story}/sub_issues -X POST -F sub_issue_id=<task's numeric id>`).
4. Non-user-facing enabling work (data generation, shared infrastructure) that doesn't map to a single FR is grouped under an **epic** issue (`type:epic`) instead of a story.
5. Update the traceability table in `PRODUCT_BRIEF.md` when a new story is added.

## Checklist

- [ ] Issue has a clear, action-oriented title (e.g. "Implement deterministic readiness checker", not "Readiness").
- [ ] Work type, priority, SDLC phase, component/agent-role labels applied per `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` label taxonomy.
- [ ] Assigned to the correct milestone (e.g. `v0.1 SDLC Demo`).
- [ ] Added to the "Support Ticket Triage Assistant" Project board with fields set (Work Type, Priority, SDLC Phase, Component/Agent, Slice).
- [ ] Description includes rationale, acceptance criteria, and any dependencies on other issues (linked by number).
- [ ] Issue size maps to a single, thin vertical slice — not a multi-week epic.
- [ ] No duplicate issue already exists for this scope.
