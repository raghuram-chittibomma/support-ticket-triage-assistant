# ADR-002: Synthetic Data Generation Approach — Hand-Curated JSON

## Status

Accepted — 2026-07-02

## Context

Issue #9 requires a documented approach for generating the synthetic product catalog, sample tickets, and knowledge base used across the demo, unit/integration tests, and evaluation scenarios (`docs/01_architecture/DATA_MODEL.md` Section 7). Two approaches were considered:

**Option A — Hand-curated JSON:** Write `data/sample/products.json`, `data/sample/tickets.json`, and `data/knowledge_base/*.json` directly as fixed, reviewable JSON files.

**Option B — Script-generated:** Write a generator script under `scripts/` that procedurally/randomly produces the same files, optionally seeded for reproducibility.

## Decision

Adopt **Option A (hand-curated JSON)** for v0.1.

## Rationale

- The v0.1 dataset is intentionally small (8 products, one sample ticket per category taxonomy entry, a handful of KB articles) — small enough to hand-author and review line by line.
- Ground-truth fields (`expected_category`, `expected_priority`, `expected_missing_fields`) must be *exactly* consistent with the deterministic rules in `DATA_MODEL.md`. Hand-curation makes that correctness auditable at review time; a generator risks silently producing ground truth that doesn't match the rules it's meant to validate.
- The same dataset serves three purposes (unit-test fixtures, integration-test input, eval ground truth per `DATA_MODEL.md` Section 7) — a fixed, version-controlled file is simpler to reason about across all three than a script whose output must be regenerated and re-verified.
- `scripts/` remains reserved for a future generator (v0.2+) if the dataset needs to scale beyond what's practical to hand-curate — e.g. for larger-scale evaluation or stress-testing the retrieval layer.

## Coverage Requirements (applies to #10, #11, #12)

- Every category in the taxonomy (`DATA_MODEL.md` Section 2) is reachable via at least one product's `category_hints` and has at least one sample ticket.
- Sample tickets include a mix of all four priority levels and both ready/not-ready readiness states, with at least one incomplete ticket per category that has a defined missing-field rule.
- Knowledge base articles cover every category likely to need a citation (Wi-Fi, Bluetooth, firmware, sound quality, subwoofer setup, warranty, returns/shipping) per issue #12's acceptance criteria.

## Data Rule

All values are fictional and invented for this project. No real customer, employer, production, or proprietary content is used as a basis for any entry — consistent with `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` Section 11 and reviewed against `.skills/synthetic-data-design.md`.

## Consequences

- Adding new sample tickets/products/KB articles going forward is a manual, reviewable edit — appropriate at this scale.
- If the dataset later needs to grow significantly (e.g. hundreds of tickets for a more rigorous eval set), revisit this decision and introduce a generator script under `scripts/`, seeded for reproducibility per `.skills/synthetic-data-design.md`.
