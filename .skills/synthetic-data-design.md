# Skill: Synthetic Data Design

Used by: Product Analyst Agent, Test/Eval Designer Agent, Main Orchestrator.

## Checklist

- [ ] No real customer, employer, company, production, or proprietary content is used as a basis for any generated example.
- [ ] Product data derives only from the fictional NorthPeak Audioworks catalog in `data/sample/products.json`.
- [ ] Generated tickets/personas are clearly fictional (no real names, addresses, emails, or order numbers resembling real systems).
- [ ] Data covers the full category taxonomy and a mix of priorities and readiness states (complete and incomplete tickets).
- [ ] Ground-truth fields (`expected_category`, `expected_priority`, `expected_missing_fields`) are consistent with the deterministic rules in `docs/01_architecture/DATA_MODEL.md`.
- [ ] Data is realistic enough to exercise the pipeline meaningfully (varied phrasing, realistic hi-fi terminology) without copying real vendor documentation.
- [ ] Generation scripts under `scripts/` are deterministic/seeded where reproducibility matters for tests.
