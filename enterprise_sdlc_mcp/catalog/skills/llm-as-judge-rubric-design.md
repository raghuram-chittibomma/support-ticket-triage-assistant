# Skill: LLM-as-Judge Rubric Design

Used by: Test/Eval Designer Agent.

## Checklist

- [ ] Rubric dimensions are explicit (e.g. faithfulness, helpfulness, policy adherence) with numeric scales.
- [ ] Pass thresholds per task type are documented in `{{project.docs.eval_strategy}}`.
- [ ] Judge prompt/rubric has a `judge_version`; changes bump the version instead of mutating history.
- [ ] Judge input includes scenario ground truth and model output — not production conversation PII (synthetic only).
- [ ] Programmatic checks remain mandatory; judge scores alone cannot pass a failing tool/outcome check (ADR-004).
- [ ] Rubric prefix is structured for prompt caching when supported (ADR-005).
- [ ] Cost of judging is noted in the milestone cost note.
