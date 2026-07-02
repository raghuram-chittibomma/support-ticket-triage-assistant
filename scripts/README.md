# scripts/

Utility scripts for generating synthetic data (product catalog, tickets, knowledge base) used by the demo, tests, and evaluation scenarios.

Per `docs/01_architecture/DECISIONS/ADR-002-synthetic-data-approach.md`, v0.1 uses **hand-curated JSON** under `data/sample/` and `data/knowledge_base/` rather than a generator script — the dataset is small enough to author and review directly, and ground-truth fields must stay exactly consistent with the deterministic rules in `DATA_MODEL.md`. This directory is reserved for a future generator script if the dataset needs to scale beyond what's practical to hand-curate (see the ADR's Consequences section).
