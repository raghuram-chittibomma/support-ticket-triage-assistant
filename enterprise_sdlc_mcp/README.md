# Enterprise SDLC MCP

Reusable build-time SDLC agent roles and skills served over Model Context Protocol (MCP).

- **Catalog:** `catalog/` — parameterized agents and skills (`{{project.*}}` placeholders).
- **Server:** `server/` — Python MCP server (`python -m enterprise_sdlc_mcp.server`).
- **Design:** `docs/01_architecture/ENTERPRISE_SDLC_MCP.md`

Consuming projects provide `sdlc.project.yaml` at the repo root and enable the server in `.cursor/mcp.json`.
