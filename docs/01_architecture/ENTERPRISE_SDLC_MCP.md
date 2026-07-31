# Enterprise SDLC MCP — Architecture

This document describes the **Enterprise SDLC MCP** program: a reusable Model Context Protocol (MCP) server that exposes build-time SDLC agent roles and skills for any GitHub-first software project. It is intentionally separate from the Support Ticket Triage Assistant **runtime product** (`src/`, `tests/` for triage behavior, `data/`).

## Purpose

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **Enterprise catalog** | Parameterized agent roles and generic SDLC skills | Standalone repo [`enterprise-sdlc-mcp`](https://github.com/raghuram-chittibomma/enterprise-sdlc-mcp), pip-installed editable into this repo's `.venv` |
| **Project overlay** | Golden rules, domain docs, domain-specific skills | `AGENTS.md`, `docs/00_project/`, `.skills/` (domain only) |
| **Runtime product** | Deployed application | `src/`, product `tests/`, `evals/` |

The catalog was originally built and vendored directly in this repo (PR [#51](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/51)). Once a second project ([`supportrouter-aws`](https://github.com/raghuram-chittibomma/supportrouter-aws)) started consuming it, it was extracted (with git history) into its own repo to remove a fragile cross-repo coupling — see [ADR-003](DECISIONS/ADR-003-extract-enterprise-sdlc-mcp.md).

Build-time agents (Code Reviewer, Solution Architect, etc.) are **not** runtime components. The MCP server delivers *what* each role checks; `AGENTS.md` still governs *when* (e.g. independent Code Reviewer before merge).

## Catalog vs overlay split

### Enterprise catalog (MCP)

**Agents (8):** product-analyst, solution-architect, implementation-planner, test-eval-designer, code-reviewer, refactor-reviewer, documentation-agent, release-manager.

**Skills (22):** requirement-tightening, github-backlog-creation, github-issue-quality-review, architecture-review, postgresql-schema-review, database-migration-review, rag-retrieval-design-review, langgraph-workflow-review, fastapi-service-review, test-eval-design, pr-code-review, release-readiness-review, readme-runbook-documentation, plus 9 added for the `supportrouter-aws` AWS/eval stack: cdk-stack-review, iam-least-privilege-review, synthetic-data-design, eval-scenario-design, llm-as-judge-rubric-design, bedrock-guardrails-review, prompt-caching-review, observability-dashboard-review, dynamodb-data-model-review.

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

1. One-time local setup: clone the catalog as a sibling directory and install it editable into this repo's own venv:
   ```bash
   git clone https://github.com/raghuram-chittibomma/enterprise-sdlc-mcp.git ../enterprise-sdlc-mcp
   .venv/Scripts/python.exe -m pip install -e ../enterprise-sdlc-mcp   # .venv/bin/python on Linux/macOS
   ```
2. `.cursor/mcp.json` runs the installed package from this repo's own `.venv`, using **absolute paths** — Cursor does not reliably resolve a relative `command` path against the workspace root on Windows (it silently falls back to the global interpreter on `PATH`, which doesn't have the package installed):
   ```json
   { "mcpServers": { "enterprise-sdlc": {
       "command": "C:\\Users\\<you>\\SDLC-Project\\.venv\\Scripts\\python.exe",
       "args": ["-m", "enterprise_sdlc_mcp.server"],
       "env": { "SDLC_PROJECT_MANIFEST": "C:\\Users\\<you>\\SDLC-Project\\sdlc.project.yaml" }
   } } }
   ```
3. Main Orchestrator calls `get_agent("code-reviewer")` before merge instead of reading `.agents/code-reviewer.md`.
4. Domain skills remain local; call `get_project_skill("hifi-audio-support-taxonomy-design.md")` when needed.

Each consuming project (this repo, `supportrouter-aws`) installs the package into its **own** venv from its **own** local clone of `enterprise-sdlc-mcp`, and its `.cursor/mcp.json` only ever references its **own** absolute paths — never another project's venv or folder.

## GitHub program differentiation

Enterprise SDLC MCP work is tracked separately from ticket-triage product slices:

- **Label:** `program:enterprise-sdlc`
- **Milestone:** `Enterprise SDLC MCP v1` (or epic under that program)
- Product triage work keeps existing `component:*`, `phase:*`, and `v0.1 SDLC Demo` milestone labels.

## Extraction (done)

Extracted to [`enterprise-sdlc-mcp`](https://github.com/raghuram-chittibomma/enterprise-sdlc-mcp) once `supportrouter-aws` became a second real consumer — see [ADR-003](DECISIONS/ADR-003-extract-enterprise-sdlc-mcp.md). This repo remains the reference implementation and first consumer; the standalone repo owns the catalog going forward.

## ADR status

This is a delivery-architecture decision for build-time tooling only. No runtime triage behavior changes. Recorded as [ADR-003](DECISIONS/ADR-003-extract-enterprise-sdlc-mcp.md).
