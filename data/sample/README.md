# data/sample/

Synthetic, hand-curated sample data for the NorthPeak Audioworks demo: product catalog and sample support tickets. See `docs/01_architecture/DECISIONS/ADR-002-synthetic-data-approach.md` for why this is hand-curated JSON rather than script-generated.

- `products.json` — the 8-product v0.1 NorthPeak Audioworks catalog (#10).
- `tickets.json` — 25 synthetic sample support tickets covering all 13 taxonomy categories, a mix of priorities, and both ready/not-ready readiness states, with eval ground-truth fields (`expected_category`, `expected_priority`, `expected_missing_fields`) (#11).

All content here is fictional. See `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` for the synthetic-data-only rule.
