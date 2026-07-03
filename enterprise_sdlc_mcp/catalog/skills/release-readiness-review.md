# Skill: Release Readiness Review

Used by: Release Manager Agent.

## Checklist

- [ ] All issues in the target milestone (e.g. `{{project.milestone.current}}`) are closed or explicitly deferred with rationale.
- [ ] CI is green on the release branch/commit.
- [ ] `{{project.docs.release_notes}}` has an entry describing what shipped and why.
- [ ] `{{project.docs.orchestrator_brief}}` open questions/assumptions are reviewed and updated if the release changed them.
- [ ] No known synthetic-data or architecture guardrail violations are outstanding.
- [ ] A GitHub Release/tag is created referencing the milestone.
