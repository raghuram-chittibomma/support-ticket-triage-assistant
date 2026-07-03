# Support Ticket Triage Assistant

An AI-assisted support ticket triage demo built for **NorthPeak Audioworks**, a fully fictional premium hi-fi audio company. This project doubles as a portfolio demonstration of running a complete, GitHub-first SDLC with the help of AI agents.

> **Status:** **v0.1.0 released** (2026-07-03) — end-to-end triage demo (pipeline, API, Gradio UI, eval suite, CI). Enterprise SDLC MCP v1 adds reusable build-time agents/skills via MCP.

## What this project is

Customer support agents at NorthPeak Audioworks receive tickets about Wi-Fi setup, Bluetooth pairing, firmware updates, speaker/amp issues, subwoofer pairing, shipping, returns, warranty, and more. This assistant takes a raw ticket description and returns:

- Ticket category and priority
- Readiness assessment (is there enough information to act on the ticket?)
- Likely issue and suggested next action
- A suggested customer response, grounded in synthetic knowledge-base references
- A confidence level and human-review flag

All product, customer, ticket, and knowledge-base data in this repository is **synthetic**. Nothing here represents a real company, real customers, or real proprietary content.

## Why this project exists

Beyond the working demo, this repository is a case study in using AI agents responsibly across the full software delivery lifecycle: requirements, architecture, backlog, implementation, testing, review, and release — with **GitHub as the source of truth** for delivery tracking and versioned docs for durable engineering artifacts.

## Start here

- [`docs/00_project/AI_ORCHESTRATOR_BRIEF.md`](docs/00_project/AI_ORCHESTRATOR_BRIEF.md) — project intent, scope, and operating rules (read this first, especially if you are an AI agent picking up this project).
- [`docs/00_project/PROJECT_CHARTER.md`](docs/00_project/PROJECT_CHARTER.md) — goals, scope, stakeholders.
- [`docs/00_project/PRODUCT_BRIEF.md`](docs/00_project/PRODUCT_BRIEF.md) — personas, requirements, taxonomy.
- [`docs/01_architecture/ARCHITECTURE.md`](docs/01_architecture/ARCHITECTURE.md) — runtime architecture.
- [`AGENTS.md`](AGENTS.md) — instructions for AI coding agents working in this repo.

## Delivery tracking

Backlog, status, and progress are tracked in the [GitHub Project board](https://github.com/users/raghuram-chittibomma/projects) and [Issues](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/issues) for this repository — not in local markdown files. See `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` for the full GitHub-first SDLC operating rule.

## Repository layout

```
docs/         durable engineering & project docs (source of truth for architecture, strategy, brief)
src/          runtime application code (FastAPI service, Gradio UI, triage pipeline) - added in later slices
tests/        pytest unit/integration tests
evals/        AI evaluation scenarios and runner
data/         synthetic product catalog, tickets, and knowledge base
scripts/      synthetic data generation scripts
db/migrations/  reserved for PostgreSQL migrations if/when adopted (not used in v0.1)
enterprise_sdlc_mcp/  Enterprise SDLC MCP server and catalog (build-time, not runtime)
.skills/      project overlay skills (domain-specific checklists only)
sdlc.project.yaml  project manifest for MCP placeholder resolution
.github/      issue/PR templates and CI workflows
```

## Tech stack (planned)

Python, FastAPI, Gradio, Pydantic, pytest, file-based synthetic data for v0.1 (PostgreSQL deferred until it adds clear value), OpenAI for LLM-assisted classification explanation and response drafting.

## License

TBD.
