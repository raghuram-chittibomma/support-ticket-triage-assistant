# Skill: Release Readiness Review

Used by: Release Manager Agent.

## Checklist

- [ ] All issues in the target milestone (e.g. `v0.1 SDLC Demo`) are closed or explicitly deferred with rationale.
- [ ] CI is green on the release branch/commit.
- [ ] `docs/03_operations/RELEASE_NOTES.md` has an entry describing what shipped and why.
- [ ] `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` open questions/assumptions are reviewed and updated if the release changed them.
- [ ] No known synthetic-data or architecture guardrail violations are outstanding.
- [ ] A GitHub Release/tag is created referencing the milestone.
