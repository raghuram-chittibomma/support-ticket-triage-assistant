# AI Orchestrator Brief — Support Ticket Triage Assistant

| Field | Value |
|---|---|
| Project name | Support Ticket Triage Assistant |
| Fictional business | NorthPeak Audioworks (synthetic premium hi-fi audio company) |
| Status | SDLC foundation established; no application code yet |
| Repository | https://github.com/raghuram-chittibomma/support-ticket-triage-assistant |
| Last reviewed | 2026-07-02 |
| Owner / Main Orchestrator | raghuram-chittibomma (single-user portfolio project) |

This document is the durable handoff brief for the Main Orchestrator Agent and any future AI agent session working on this project. It preserves original intent so that context is not lost between chat sessions. It is **not** a backlog — for current work items and status, see the GitHub Project board and Issues linked below.

## 1. Fictional Business Context

**NorthPeak Audioworks** is a fully synthetic, direct-to-consumer premium home audio company invented for this project. It sells passive and powered bookshelf speakers, network streamers, DACs, integrated amplifiers, subwoofers, speaker stands, room calibration accessories, and cables/setup accessories.

The synthetic v0.1 product catalog (refined from the original brainstorm; final version lives in `data/sample/products.json`):

- **Summit One Bookshelf** — passive bookshelf speaker (placement, distortion, amp pairing)
- **Summit One Active** — powered bookshelf speaker (Wi-Fi setup, Bluetooth pairing, app setup)
- **Cedar 200 Integrated Amp** — integrated amplifier (hum, input selection, speaker matching)
- **Cedar Stream Mini** — network streamer (Spotify Connect, AirPlay, network discovery)
- **AeroDAC 2** — USB/Bluetooth DAC (USB recognition, Bluetooth codec questions)
- **RidgeSub 8** — compact subwoofer (pairing, crossover, placement, low output)
- **PeakStand 24** — speaker stand (assembly, compatibility, missing parts)
- **RoomTune Mic** — room calibration microphone (calibration setup, app recognition)

No real company, product, customer, or proprietary content is used anywhere in this project. See Section 8 (Synthetic-Data-Only Rule).

## 2. Project Purpose

Build an AI assistant that helps the NorthPeak Audioworks support team triage incoming customer support tickets — while using the build itself as a demonstration of a disciplined, GitHub-first, AI-assisted SDLC that a PM/TPM can drive end to end.

## 3. Business Goal

Reduce time spent manually reviewing support tickets by helping support agents quickly classify tickets, identify missing information, surface relevant knowledge, and draft consistent customer responses.

## 4. Target Users

- **Primary:** Customer support agent.
- **Secondary:** Support lead, product owner, QA analyst, engineering support team.

## 5. Initial v0.1 Scope

A user submits a ticket description. The system returns: category, priority, readiness/missing-information assessment, likely issue, suggested next action, suggested customer response, relevant FAQ/policy/troubleshooting references, confidence level, and a human-review flag.

v0.1 explicitly excludes: authentication/multi-user, ticket persistence/history, real integrations, semantic (vector) retrieval, LangGraph orchestration, and PostgreSQL — see the Architecture Decision Record for rationale (`docs/01_architecture/ADR-001-architecture-choice.md`).

## 6. GitHub-First SDLC Operating Rule

GitHub is the **primary source of truth for delivery tracking**. It owns:

- Requirements backlog, issues, features/stories/tasks, acceptance criteria
- Milestones, the Project board, status tracking, labels
- Pull requests, release notes, delivery traceability

The GitHub Project board for this repository is **"Support Ticket Triage Assistant"** (user-owned, linked to this repo). The first milestone is **`v0.1 SDLC Demo`**.

Local repository docs are created **only** when: (1) GitHub has no suitable native home for the artifact, (2) the artifact must be version-controlled with the code, or (3) it is a durable engineering/project document (architecture, ADRs, test/eval strategy, runbook, release notes, this brief). Local docs must never duplicate GitHub issue tracking — at most, they may link to the relevant milestone/Project view.

## 7. Source-of-Truth Rules

| Concern | Source of truth |
|---|---|
| Requirements/backlog | GitHub Issues + Project board |
| Architecture | `docs/01_architecture/ARCHITECTURE.md` + ADRs |
| Data model | `docs/01_architecture/DATA_MODEL.md` |
| Testing/evaluation strategy | `docs/02_testing/TEST_STRATEGY.md`, `EVAL_STRATEGY.md` |
| Test/eval results | CI runs and `evals/` output (not restated in docs) |
| Release | GitHub Releases/tags (facts) + `docs/03_operations/RELEASE_NOTES.md` (human-readable log) |
| Project initiation/intent | This document |

## 8. Build-Time SDLC Agents vs. Runtime Product Components

This project uses "agent" in two distinct senses that must never be conflated:

**Build-time SDLC agents** (defined under `.agents/`) are reusable AI assistant roles that help *build and manage* this project: Product Analyst, Solution Architect, Implementation Planner, Test/Eval Designer, Code Reviewer, Refactor Reviewer, Documentation Agent, Release Manager. They are **not part of the deployed application**. They support the Main Orchestrator and do not independently set conflicting project direction. Most are advisory/document-producing; only the Test/Eval Designer writes code, and only under `tests/`/`evals/`.

**Runtime product components** (defined under `src/`) are parts of the actual triage application: ticket readiness checker, missing-information detector, ticket classifier, priority estimator, knowledge retriever, response drafter, confidence scorer, human-review decision logic, and the pipeline that orchestrates them.

Rule: do not create application code for build-time SDLC agents. Do not describe runtime components as "agents" performing SDLC work.

## 9. Preferred Technology Stack

Python, FastAPI (service/API layer), Gradio (demo UI), Pydantic (schemas/validation), pytest (tests), OpenAI (LLM provider for classification explanation, response drafting, and ambiguity handling — configured behind a thin client so it can be swapped later). LangGraph and ChromaDB are **not used in v0.1** (no clear value yet for a fixed linear pipeline over a small KB) but are documented extension points for v0.2+. GitHub Issues/Projects for SDLC tracking; GitHub Actions for CI.

## 10. PostgreSQL Rule

If relational persistence is needed, use PostgreSQL — never SQLite for application persistence (SQLite is permitted only for clearly justified, temporary local testing). For v0.1, file-based synthetic data is sufficient and PostgreSQL is **not used**. If PostgreSQL is adopted later (e.g. for ticket history, audit trail, evaluation-run tracking, or feedback), schema changes must go through migration files under `db/migrations/`, never ad hoc manual schema edits.

## 11. Synthetic-Data-Only Rule

All data in this repository — product catalog, customer personas, support tickets, FAQ/policy/troubleshooting content, firmware release notes, evaluation scenarios, and historical examples — must be synthetic and fictional. Never use real customer data, real employer/company data, real production logs, real product manuals, or copied proprietary knowledge base content.

## 12. Initial Constraints

- Single-user portfolio/demo project — avoid unnecessary enterprise complexity.
- Use AI only where it adds clear value; prefer deterministic rules for readiness checks, schema validation, routing, and quality gates.
- Only one agent modifies code during a given implementation slice, unless explicitly instructed otherwise.
- Local-first development.

## 13. Expected Project Artifacts

Local (version-controlled): this brief, `PROJECT_CHARTER.md`, `PRODUCT_BRIEF.md`, `ARCHITECTURE.md`, `DATA_MODEL.md`, ADRs, `TEST_STRATEGY.md`, `EVAL_STRATEGY.md`, `RUNBOOK.md`, `RELEASE_NOTES.md`, `AGENTS.md`, `.agents/*`, `.skills/*`.

GitHub-native: labels, milestones, Project board, issues, pull requests, releases.

## 14. Expected SDLC Workflow

1. Requirement captured/refined → GitHub Issue created (Product Analyst Agent assists).
2. Architecture/design decisions recorded in `docs/01_architecture/` (Solution Architect Agent assists).
3. Issue broken into an implementation slice (Implementation Planner Agent assists).
4. Main Orchestrator implements the slice on a feature branch named after the issue.
5. Tests/evals added (Test/Eval Designer Agent assists).
6. PR opened referencing `Closes #<issue>`; reviewed by an **independent Code Reviewer subagent** (fresh context, not the Main Orchestrator self-reviewing its own diff) — see `.agents/code-reviewer.md` Trigger Mechanism. Refactor Reviewer subagent invoked periodically or when structural concerns arise.
7. CI passes; findings addressed; PR merged; issue closed.
8. Docs updated if architecture/behavior changed (Documentation Agent assists).
9. Release cut and `RELEASE_NOTES.md` updated (Release Manager Agent assists).

## 15. Initial Assumptions

- Single ticket processed at a time; no batch processing in v0.1.
- English-language tickets only.
- An OpenAI API key is available via environment variable for local development; no key is committed to the repo.
- No PII exists anywhere in the project because all data is synthetic.
- A single developer (assisted by AI agents) drives delivery; no team-scale process overhead is needed.

## 16. Open Questions

- Exact weighting formula for the confidence score (classifier confidence vs. readiness vs. retrieval match strength) — to be resolved during Slice 2–4 design.
- Whether a v0.2 needs PostgreSQL for evaluation-run history/audit trail, or whether file-based eval logs remain sufficient longer.
- Whether semantic (vector) retrieval becomes worthwhile once the knowledge base grows beyond a small curated set.
- Whether LangGraph becomes worthwhile if the pipeline gains branching/looping behavior (e.g., iterative clarification with the user).

This section should be revisited at each milestone; do not let it go stale.

## 17. How AI Agents and Skills Are Used During Delivery

Build-time SDLC agent roles are defined under `.agents/` (see Section 8). Reusable checklists/skills that any agent or the Main Orchestrator can apply are defined under `.skills/` — e.g. requirement tightening, GitHub backlog creation, GitHub issue quality review, architecture review, synthetic data design, hi-fi audio support taxonomy design, ticket readiness rule design, FastAPI service review, test/eval design, PR/code review, release readiness review. Agents advise, draft, and review; the Main Orchestrator remains responsible for final direction and for any given slice's code changes.
