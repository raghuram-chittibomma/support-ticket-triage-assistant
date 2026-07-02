# AGENTS.md — Instructions for AI Coding Agents

This file gives any AI coding agent (Cursor, Claude, Copilot, etc.) the operating rules for working in this repository. Read this before making changes. For full project context, also read [`docs/00_project/AI_ORCHESTRATOR_BRIEF.md`](docs/00_project/AI_ORCHESTRATOR_BRIEF.md).

## Project in one paragraph

This is a synthetic AI support-ticket triage assistant for a fictional hi-fi audio company, NorthPeak Audioworks. It is also a demonstration of an AI-assisted, GitHub-first SDLC. All data (products, tickets, customers, knowledge base) must be synthetic — never real.

## Golden rules

1. **GitHub is the source of truth for delivery tracking.** Issues, the Project board, milestones, and PRs track backlog and status. Do not create local markdown files that duplicate issue tracking. Local docs are only for durable artifacts (architecture, ADRs, strategy, brief, runbook, release notes).
2. **Synthetic data only.** Never introduce real customer, employer, company, production, or proprietary content. All product names (e.g. Summit One Bookshelf, Cedar 200 Integrated Amp), customers, tickets, and KB articles are fictional and invented for this project.
3. **Build-time SDLC agents are not runtime product components.** Roles defined under `.agents/` (Product Analyst, Solution Architect, Implementation Planner, Test/Eval Designer, Code Reviewer, Refactor Reviewer, Documentation Agent, Release Manager) assist with *building* this project. They are never part of the deployed application. Runtime components (classifier, priority estimator, retriever, response drafter, etc.) live under `src/` and are designed independently — see `docs/01_architecture/ARCHITECTURE.md`.
4. **Prefer deterministic logic for rules, LLM reasoning for language tasks.** Readiness checks, missing-information detection, priority scoring, and routing should be deterministic and explainable. Use an LLM for classification explanation, response drafting, summarization, and ambiguity handling.
5. **PostgreSQL only if it earns its place.** Do not introduce PostgreSQL (or any database) unless a specific requirement needs relational persistence. If/when adopted, manage schema changes through migration files under `db/migrations/` — never ad hoc manual schema edits. Do not use SQLite for application persistence except as clearly justified, temporary local testing.
6. **One agent modifies code per implementation slice**, unless a task explicitly says otherwise. Avoid touching files outside the scope of the current issue/slice.
7. **Every change traces back to a GitHub issue, and every task traces back to a user story.** Backlog issues follow a Story -> Task hierarchy (see `.skills/github-backlog-creation.md`) linked via GitHub sub-issues, not a flat, architecture-shaped task list. Branch names should reference the task issue (e.g. `issue-14-readiness-checker`), and PRs should include `Closes #<issue-number>`.
8. **Tests/evals are part of the definition of done.** New runtime behavior needs corresponding tests under `tests/` and, where relevant, eval scenarios under `evals/`.

## Where things live

- `docs/00_project/` — project initiation brief, charter, product brief.
- `docs/01_architecture/` — architecture, data model, ADRs.
- `docs/02_testing/` — test strategy, evaluation strategy.
- `docs/03_operations/` — runbook, release notes.
- `src/` — runtime application code only.
- `tests/`, `evals/` — test and evaluation code.
- `data/sample/`, `data/knowledge_base/`, `data/generated/` — synthetic data.
- `scripts/` — synthetic data generation utilities.
- `.agents/` — build-time SDLC agent role definitions (reference only, not imported by application code).
- `.skills/` — reusable build-time checklists used during delivery.

## Before opening a PR

- Confirm the change maps to an open GitHub issue in the `v0.1 SDLC Demo` milestone (or a later milestone).
- Run `pytest` and ensure it passes.
- Update relevant docs under `docs/` if architecture, data model, or strategy changed.
- Do not restate GitHub issue status in local markdown files.
