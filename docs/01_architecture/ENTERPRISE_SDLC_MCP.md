# Enterprise SDLC MCP — Architecture

This document describes the **Enterprise SDLC MCP** program: a reusable Model Context Protocol (MCP) server that exposes build-time SDLC agent roles and skills for any GitHub-first software project. It is intentionally separate from the Support Ticket Triage Assistant **runtime product** (`src/`, `tests/` for triage behavior, `data/`).

## Purpose

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **Enterprise catalog** | Parameterized agent roles and generic SDLC skills | `enterprise-sdlc-mcp/catalog/` served by MCP |
| **Project overlay** | Golden rules, domain docs, domain-specific skills | `AGENTS.md`, `docs/00_project/`, `.skills/` (domain only) |
| **Runtime product** | Deployed application | `src/`, product `tests/`, `evals/` |

Build-time agents (Code Reviewer, Solution Architect, etc.) are **not** runtime components. The MCP server delivers *what* each role checks; `AGENTS.md` still governs *when* (e.g. independent Code Reviewer before merge).

## Catalog vs overlay split

### Enterprise catalog (MCP)

**Agents (8):** product-analyst, solution-architect, implementation-planner, test-eval-designer, code-reviewer, refactor-reviewer, documentation-agent, release-manager.

**Skills (13):** requirement-tightening, github-backlog-creation, github-issue-quality-review, architecture-review, postgresql-schema-review, database-migration-review, rag-retrieval-design-review, langgraph-workflow-review, fastapi-service-review, test-eval-design, pr-code-review, release-readiness-review, readme-runbook-documentation.

Catalog markdown uses `{{project.*}}` placeholders resolved at serve time from a project manifest.

### Project overlay (local)

- `AGENTS.md` — project golden rules and consumption instructions.
- `docs/00_project/`, `docs/01_architecture/`, etc. — domain architecture and briefs.
- `.skills/` — domain-only skills:
  - `hifi-audio-support-taxonomy-design.md`
  - `ticket-readiness-rule-design.md`
  - `synthetic-data-design.md`

## Parameterization

Each consuming repo provides `sdlc.project.yaml` at its root:

```yaml
display_name: Support Ticket Triage Assistant
docs:
  architecture: docs/01_architecture/ARCHITECTURE.md
  data_model: docs/01_architecture/DATA_MODEL.md
  # ...
paths:
  source: src/
  tests: tests/
  project_skills: .skills/
milestone:
  current: v0.1 SDLC Demo
extensions:
  - LLMClient
  - Retriever
  - TriageRepository
```

Placeholders in catalog templates:

| Placeholder | Example resolved value |
|-------------|------------------------|
| `{{project.display_name}}` | Support Ticket Triage Assistant |
| `{{project.docs.architecture}}` | docs/01_architecture/ARCHITECTURE.md |
| `{{project.paths.source}}` | src/ |
| `{{project.extensions}}` | LLMClient, Retriever, TriageRepository |

Resolution is deterministic string substitution — no LLM involved.

## MCP surface

**Server:** `enterprise-sdlc-mcp` (stdio transport via `.cursor/mcp.json`).

### Tools

| Tool | Description |
|------|-------------|
| `list_agents` | Catalog agent IDs, titles, and one-line purpose |
| `get_agent` | Resolved agent role markdown for a project |
| `list_skills` | Catalog skill IDs and titles |
| `get_skill` | Resolved skill checklist for a project |
| `list_project_skills` | Domain skills from project overlay path |
| `get_project_skill` | Read a project-local skill file |
| `get_project_manifest` | Parsed and validated project manifest |

### Resources

| URI pattern | Content |
|-------------|---------|
| `enterprise-sdlc://catalog/manifest` | Catalog manifest JSON |
| `enterprise-sdlc://agents/{id}` | Resolved agent (requires manifest env or default) |
| `enterprise-sdlc://skills/{id}` | Resolved skill |

### Prompts

| Prompt | Use |
|--------|-----|
| `independent_code_review` | Launch Code Reviewer subagent with resolved role + pr-code-review skill |
| `architecture_review` | Launch Solution Architect / Refactor Reviewer review pass |

## Consumption in Cursor

1. Enable MCP server in `.cursor/mcp.json` (points at `enterprise-sdlc-mcp` package).
2. Set `SDLC_PROJECT_MANIFEST` to the repo's `sdlc.project.yaml` (configured in mcp.json `env`).
3. Main Orchestrator calls `get_agent("code-reviewer")` before merge instead of reading `.agents/code-reviewer.md`.
4. Domain skills remain local; call `get_project_skill("hifi-audio-support-taxonomy-design.md")` when needed.

Use the project's Python interpreter (e.g. activate `.venv` first, or point `command` at `.venv/Scripts/python.exe` on Windows / `.venv/bin/python` on Linux/macOS if Cursor does not pick up the venv automatically).

## GitHub program differentiation

Enterprise SDLC MCP work is tracked separately from ticket-triage product slices:

- **Label:** `program:enterprise-sdlc`
- **Milestone:** `Enterprise SDLC MCP v1` (or epic under that program)
- Product triage work keeps existing `component:*`, `phase:*`, and `v0.1 SDLC Demo` milestone labels.

## Future extraction

The `enterprise-sdlc-mcp/` directory is structured to become a standalone repository or installable package. This repo acts as the first consumer and reference implementation.

## ADR status

This is a delivery-architecture decision for build-time tooling only. No runtime triage behavior changes. If the MCP catalog becomes the sole source for agent definitions across multiple repos, record ADR-003.
