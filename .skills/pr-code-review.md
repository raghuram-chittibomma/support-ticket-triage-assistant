# Skill: PR/Code Review

Used by: Code Reviewer Agent.

## Checklist

- [ ] PR references its GitHub issue (`Closes #<n>`).
- [ ] PR touches only files in scope for the linked issue — no unrelated changes.
- [ ] Tests/evals are included per the Definition of Done and pass in CI.
- [ ] Docs updated if architecture, data model, or operational behavior changed.
- [ ] No real/sensitive data introduced anywhere in the diff.
- [ ] Only one agent's code changes are present in the PR, consistent with the one-agent-per-slice rule (unless explicitly a multi-agent exception).
