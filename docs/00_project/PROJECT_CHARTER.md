# Project Charter — Support Ticket Triage Assistant

## Purpose

Deliver a working AI-assisted support ticket triage demo for the fictional company NorthPeak Audioworks, while demonstrating a disciplined, GitHub-first SDLC that a PM/TPM can drive with the help of AI agents.

## Business Case

NorthPeak Audioworks support agents spend significant time manually reading tickets, deciding on category/priority, checking whether enough information was provided, and searching for the right FAQ/policy content before responding. This is slow and inconsistent. An AI triage assistant reduces manual review time and improves response consistency.

## Goals

1. Ship a v0.1 demo that takes a raw ticket description and returns category, priority, readiness, likely issue, next action, a draft response, references, confidence, and a human-review flag.
2. Demonstrate a complete, auditable, GitHub-first SDLC (requirements → issues → branches → PRs → tests → release).
3. Keep the codebase small, explainable, and free of unnecessary complexity appropriate for a single-user portfolio project.

## Non-Goals (v0.1)

- Production deployment, authentication, or multi-tenant support.
- Ticket persistence, history, or audit trail (deferred; PostgreSQL not used in v0.1).
- Real integrations with a helpdesk system, CRM, or messaging platform.
- Multilingual ticket support.

## Stakeholders

| Role | Interest |
|---|---|
| Project owner / Main Orchestrator (raghuram-chittibomma) | Overall delivery, direction, final sign-off |
| Customer support agent (persona) | Primary end user of the triage output |
| Support lead (persona) | Oversight of triage quality and escalations |
| Product owner (persona) | Scope and roadmap decisions |
| QA analyst (persona) | Test/eval coverage and quality gates |
| Engineering support (persona) | Maintainability, architecture soundness |

## Success Criteria for v0.1

- A ticket can be submitted (via CLI or minimal UI) and a complete triage result is returned.
- Deterministic rules (readiness, missing-info, priority, human-review gate) are unit-tested.
- Classification and drafting are evaluated against a synthetic scenario set with acceptable accuracy (see `docs/02_testing/EVAL_STRATEGY.md`).
- All backlog items for the `v0.1 SDLC Demo` milestone are tracked and closed via GitHub Issues/PRs.
- `docs/03_operations/RELEASE_NOTES.md` documents the v0.1 release.

## Constraints

See `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` Section 12 for the full constraint list (synthetic data only, PostgreSQL rule, one-agent-per-slice rule, GitHub-first tracking, avoid unnecessary complexity).

## Governance

GitHub Issues and the "Support Ticket Triage Assistant" Project board are the source of truth for scope and status. This charter and the orchestrator brief are reviewed at each milestone boundary and updated if scope materially changes.
