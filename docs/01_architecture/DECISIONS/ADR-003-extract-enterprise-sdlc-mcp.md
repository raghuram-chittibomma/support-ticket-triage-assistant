# ADR-003: Extract Enterprise SDLC MCP into a Standalone Repo/Package

## Status

Accepted — 2026-07-31

## Context

The Enterprise SDLC MCP catalog (8 build-time agent roles, 22 generic/technical SDLC skills) was originally built and vendored directly in this repo under `enterprise_sdlc_mcp/` (PR [#51](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/51)), with `docs/01_architecture/ENTERPRISE_SDLC_MCP.md` explicitly flagging future extraction as the intended path once a second consumer existed.

That condition was met: [`supportrouter-aws`](https://github.com/raghuram-chittibomma/supportrouter-aws) started consuming the same catalog, but its `.cursor/mcp.json` pointed directly at this repo's own `.venv` interpreter and folder path (`C:\Users\raghu\SDLC-Project\...`) across the filesystem. That coupling was fragile: renaming, moving, or rebuilding this repo's venv would silently break the other project's MCP server. In addition, nine catalog skill files (`cdk-stack-review`, `bedrock-guardrails-review`, etc.) added to support `supportrouter-aws` existed only on local disk in this repo, never committed to git — a second, sharper version of the same problem.

Two extraction approaches were considered:

**Option A — Git submodule / shared folder path.** Move the folder to a shared location on disk, reference it via a fixed path or git submodule from each consumer.

**Option B — Standalone installable Python package, consumed via editable local install.** Give the extracted code its own `pyproject.toml`, console-script entry point, and test suite in its own repo; each consuming project clones it as a sibling directory and runs `pip install -e ../enterprise-sdlc-mcp` into its own venv.

## Decision

Adopt **Option B**. Extract `enterprise_sdlc_mcp/` (with git history, via `git subtree split`) into the standalone repo [`enterprise-sdlc-mcp`](https://github.com/raghuram-chittibomma/enterprise-sdlc-mcp), tagged `v0.1.0`. Remove the vendored folder from this repo and from `supportrouter-aws`; both now install the package editable into their own `.venv` from their own local clone.

## Rationale

- Each consuming project owns its own dependency on a versioned package — no project's tooling depends on another project's filesystem layout, venv, or continued existence at a specific path.
- `resolver.py`'s catalog/path resolution already worked relative to the package's own `__file__` rather than the consuming repo, so extraction required no behavioral rewrite beyond fixing one now-incorrect `repo_root()` helper (previously assumed the package lived one level inside a consumer's repo; now the package *is* the repo root).
- Editable local installs (`pip install -e`) keep the same "clone a sibling directory, no registry needed" simplicity as folder-vendoring, while giving the package a real identity: its own tests, its own CI, its own version tag, its own README documenting what it is independent of any one consumer.
- A pip-registry-hosted dependency (Option not pursued) was rejected as unnecessary ceremony for a personal multi-repo setup with no external distribution need yet.

## Consequences

- `SDLC-Project`'s `pyproject.toml` no longer lists `mcp`/`pyyaml` as its own dependencies (they come transitively via the externally-installed package); `.cursor/mcp.json` now runs `.venv/Scripts/python.exe -m enterprise_sdlc_mcp.server` with no `PYTHONPATH`.
- The moved test suite (`tests/enterprise_sdlc_mcp/`) now lives in the standalone repo's own `tests/`, tested against a fixture manifest rather than this repo's `sdlc.project.yaml`.
- If the catalog is ever consumed by a project on a different machine, or needs CI-time installation, revisit this decision to publish to a package index or pin via a git-URL dependency instead of a local sibling clone.
- Tracked under `program:enterprise-sdlc` via issue [#65](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/issues/65).
