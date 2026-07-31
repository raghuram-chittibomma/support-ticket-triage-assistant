# Skill: Synthetic Data Design

Used by: Product Analyst Agent, Test/Eval Designer Agent.

## Checklist

- [ ] No real customer, employer, company, production, or proprietary content is used as a basis for any fixture.
- [ ] Product/order/persona data derives only from the fictional domain described in `{{project.docs.orchestrator_brief}}` / `{{project.docs.data_model}}`.
- [ ] Generated names, emails, addresses, and order IDs are clearly fictional.
- [ ] Knowledge base / policy articles are original synthetic text — not copied from real manuals or vendor docs.
- [ ] Ground-truth fields in fixtures align with deterministic rules in `{{project.docs.data_model}}`.
- [ ] Data is realistic enough for demos/tests/evals without representing real people or confidential workflows.
- [ ] Generation scripts under `scripts/` are seeded/deterministic where reproducibility matters.
- [ ] Eval datasets under `{{project.paths.evals}}` are not reused as few-shot examples in runtime prompts.
