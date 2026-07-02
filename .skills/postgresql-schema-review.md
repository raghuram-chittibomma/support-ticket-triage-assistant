# Skill: PostgreSQL Schema Review

Used by: Solution Architect Agent. Applies only if/when PostgreSQL is adopted (not used in v0.1 — see `docs/01_architecture/DECISIONS/ADR-001-architecture-choice.md`).

## Checklist

- [ ] A real requirement (not speculative) justifies relational persistence — documented in an ADR.
- [ ] Schema matches the forward-looking design in `docs/01_architecture/DATA_MODEL.md` Section 8, or that section is updated to match.
- [ ] Primary keys, foreign keys, and indexes are defined for expected query patterns (e.g. ticket lookups, eval-run history).
- [ ] No PII or real customer data can enter any table — schema and seed data remain synthetic.
- [ ] Schema changes are introduced only via migration files (see `database-migration-review.md`), never manual edits.
- [ ] SQLite is not used for application persistence except explicitly justified temporary local testing.
