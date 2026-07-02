# db/migrations/

Reserved for PostgreSQL schema migration files.

**Not used in v0.1.** Per `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` and `docs/01_architecture/ADR-001-architecture-choice.md`, v0.1 uses file-based synthetic data and has no relational persistence requirement. If a later version introduces PostgreSQL (e.g. for ticket history, audit trail, or evaluation-run tracking), schema changes must be introduced through migration files here — never ad hoc manual schema edits. See the database-migration-review skill (`.skills/database-migration-review.md`) before adding migrations.
