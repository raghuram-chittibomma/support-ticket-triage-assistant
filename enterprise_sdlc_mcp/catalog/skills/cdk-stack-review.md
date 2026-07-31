# Skill: CDK Stack Review

Used by: Solution Architect Agent, Code Reviewer Agent.

## Checklist

- [ ] Every AWS resource for this change is defined in CDK under `{{project.paths.infra}}` — no console-created resources.
- [ ] Stacks are split so runtime and eval-plane concerns can evolve independently when both exist.
- [ ] Removal/teardown path exists (`scripts/teardown` or documented `cdk destroy`) and is mentioned in the issue cost note.
- [ ] Environment/account/region assumptions match `{{project.docs.architecture}}` and ADRs.
- [ ] No hardcoded secrets; parameters/SSM/Secrets Manager used appropriately.
- [ ] Resource names/tags include project identifier for cost attribution.
- [ ] Lambda package sizes and timeouts are realistic for LangGraph cold starts.
