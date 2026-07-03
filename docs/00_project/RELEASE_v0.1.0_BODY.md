# v0.1.0 — Agentic SDLC case study

**Portfolio artifact:** end-to-end delivery of a small LLM demo using AI coding agents, GitHub as source of truth, and explicit quality gates. The triage app is the **demo vehicle**; the **process** is what this release documents.

## How this was delivered

- **Backlog:** FR → user stories → tasks on GitHub Issues (see [`PRODUCT_BRIEF.md`](docs/00_project/PRODUCT_BRIEF.md))
- **Slices:** 7 product PRs ([#38](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/38)–[#46](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/46)) + eval, CI, release infrastructure
- **Review:** independent Code Reviewer subagent before every merge — blocking bugs caught in [#40](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/40), [#42](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/42), [#43](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/43) (see [`RELEASE_NOTES.md`](docs/03_operations/RELEASE_NOTES.md))
- **Agent tooling:** Enterprise SDLC MCP v1 ([#51](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/51)) — reusable build-time roles/skills, dogfooded from [#53](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/53) onward
- **Quality gates:** 273-test pytest suite (`pytest -m "not llm"`), fixture eval baseline, GitHub Actions CI on every PR

**Start here for reviewers:** [`PORTFOLIO_TOUR.md`](docs/00_project/PORTFOLIO_TOUR.md) · [`DELIVERY_RECORD.md`](docs/00_project/DELIVERY_RECORD.md)

## Demo vehicle (runtime product)

End-to-end triage pipeline — classification, readiness, priority, KB retrieval, response drafting, confidence, human-review — via FastAPI (`POST /triage`) and Gradio UI. All data synthetic; deterministic rules for gates/scoring; LLM for classification explanation and response drafting only.

**Quick start:** [`RUNBOOK.md`](docs/03_operations/RUNBOOK.md) — `python -m src.ui` (requires `OPENAI_API_KEY`).

## Full release log

[`RELEASE_NOTES.md` — v0.1.0 section](docs/03_operations/RELEASE_NOTES.md#v010--sdlc-demo)

## Deferred (honest backlog)

- [#39](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/issues/39) — Harden missing-info keyword rules (P2)
- [#41](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/issues/41) — Stale doc reference in PostgreSQL schema review skill (P3)
