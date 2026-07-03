# Skill: PostgreSQL Schema Review

Used by: Solution Architect Agent. Applies only if/when PostgreSQL is adopted.

## Checklist

- [ ] A real requirement (not speculative) justifies relational persistence — documented in an ADR.
- [ ] Schema matches the forward-looking design in `{{project.docs.data_model}}`, or that doc is updated to match.
- [ ] Primary keys, foreign keys, and indexes are defined for expected query patterns.
- [ ] No PII or real customer data can enter any table — schema and seed data remain synthetic.
- [ ] Schema changes are introduced only via migration files (see database-migration-review skill), never manual edits.
- [ ] SQLite is not used for application persistence except explicitly justified temporary local testing.
