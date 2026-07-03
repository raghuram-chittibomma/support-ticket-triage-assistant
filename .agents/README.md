# Build-Time SDLC Agents (Enterprise MCP)

Enterprise build-time agent role definitions have moved to the **Enterprise SDLC MCP** catalog.

Use MCP tools instead of local files:

- `list_agents()` — catalog index
- `get_agent("code-reviewer")` — resolved role for this project
- Prompt `independent_code_review` — launch independent review subagent

See `AGENTS.md`, `sdlc.project.yaml`, and `docs/01_architecture/ENTERPRISE_SDLC_MCP.md`.

Local `.agents/` is retained only as a pointer; do not add duplicate role definitions here.
