# Skill: Bedrock Guardrails Review

Used by: Solution Architect Agent, Code Reviewer Agent.

## Checklist

- [ ] Guardrail covers PII filtering, denied topics, and no financial-advice style policies agreed in product docs.
- [ ] Input and output paths both apply Guardrails (or documented exception with compensating control).
- [ ] Deterministic app-level validation still runs for IDs, refund thresholds, and schema checks.
- [ ] Block/escalate behavior is tested with synthetic adversarial prompts.
- [ ] Guardrail identifier/version is recorded in session/observability traces.
- [ ] Changes to Guardrail config are eval-gated when they affect user-visible answers.
