# Skill: IAM Least-Privilege Review

Used by: Solution Architect Agent, Code Reviewer Agent.

## Checklist

- [ ] Each Lambda tool has its **own** execution role (not a shared god-role).
- [ ] Refund/write tools can touch only their required table(s)/queue(s) — no broad `dynamodb:*` on `*`.
- [ ] Read-only tools cannot invoke refund or mutate approvals.
- [ ] Bedrock invoke permissions are scoped to required model IDs / Knowledge Base IDs where possible.
- [ ] Step Functions / EventBridge roles follow least privilege for eval fan-out only.
- [ ] No long-lived access keys in code or CI; prefer OIDC / role assumption.
- [ ] IAM changes are reviewed in the same PR as the resource that needs them.
