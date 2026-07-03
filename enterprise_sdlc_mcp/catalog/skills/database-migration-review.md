# Skill: Database Migration Review

Used by: Solution Architect Agent, Code Reviewer Agent. Applies only if/when PostgreSQL is adopted.

## Checklist

- [ ] Migration is a new, timestamped/ordered file under `{{project.paths.migrations}}` — never an edit to a previously-applied migration.
- [ ] Migration is reversible (has an explicit down/rollback path) where feasible.
- [ ] Migration matches the schema documented in `{{project.docs.data_model}}`; the doc is updated in the same PR if the schema changed.
- [ ] No destructive change (drop/alter losing data) ships without explicit confirmation and a noted rationale.
- [ ] Migration has been run locally against a disposable database before merge.
