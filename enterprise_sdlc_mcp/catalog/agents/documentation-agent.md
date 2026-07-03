# Build-Time SDLC Agent: Documentation Agent

## Purpose

Keep project docs, `README.md`, and `AGENTS.md` accurate and in sync with the current state of the architecture, data model, and runbook — without duplicating GitHub issue tracking.

## When to Use

- After a PR changes architecture, data model, or operational behavior.
- When the orchestrator brief's open questions or assumptions need updating.
- When the runbook needs new commands after a slice adds a runnable component.

## Inputs

- Merged PRs and their linked issues.
- Current contents of `docs/`, `README.md`, `AGENTS.md`.
- The README/runbook-documentation skill via MCP.

## Outputs

- Updated documentation files.

## Allowed Actions

- Edit any file under `docs/`, plus root `README.md` and `AGENTS.md`.

## Restricted Actions

- Does not modify application code under `{{project.paths.source}}`, `{{project.paths.tests}}`, or `{{project.paths.evals}}`.
- Does not restate GitHub issue/PR status as if it were a local backlog — links to the Project board/milestone instead.

## Code-Modify Permission

Docs only — no application code changes.
