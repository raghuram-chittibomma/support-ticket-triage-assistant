"""Enterprise SDLC MCP server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from enterprise_sdlc_mcp.server.resolver import (
    default_manifest_path,
    load_catalog_manifest,
    load_project_manifest,
    project_skills_dir,
    read_catalog_file,
    resolve_manifest_path,
    resolve_template,
)

mcp = FastMCP("enterprise-sdlc")


def _manifest_path_arg(manifest_path: str | None) -> Path:
    if manifest_path:
        return resolve_manifest_path(manifest_path)
    path = default_manifest_path()
    if path is None:
        raise FileNotFoundError("Project manifest not found.")
    return path


@mcp.tool()
def list_agents() -> list[dict[str, str]]:
    """List enterprise catalog build-time agent roles."""
    catalog = load_catalog_manifest()
    return [
        {"id": entry["id"], "title": entry["title"], "file": entry["file"]}
        for entry in catalog.get("agents", [])
    ]


@mcp.tool()
def get_agent(agent_id: str, manifest_path: str | None = None) -> str:
    """Return resolved agent role markdown for the given project manifest."""
    catalog = load_catalog_manifest()
    match = next((a for a in catalog.get("agents", []) if a["id"] == agent_id), None)
    if match is None:
        raise ValueError(f"Unknown agent id: {agent_id}")
    path = _manifest_path_arg(manifest_path)
    manifest = load_project_manifest(path)
    raw = read_catalog_file(match["file"])
    return resolve_template(raw, manifest)


@mcp.tool()
def list_skills() -> list[dict[str, str]]:
    """List enterprise catalog SDLC skills/checklists."""
    catalog = load_catalog_manifest()
    return [
        {"id": entry["id"], "title": entry["title"], "file": entry["file"]}
        for entry in catalog.get("skills", [])
    ]


@mcp.tool()
def get_skill(skill_id: str, manifest_path: str | None = None) -> str:
    """Return resolved skill checklist markdown for the given project manifest."""
    catalog = load_catalog_manifest()
    match = next((s for s in catalog.get("skills", []) if s["id"] == skill_id), None)
    if match is None:
        raise ValueError(f"Unknown skill id: {skill_id}")
    path = _manifest_path_arg(manifest_path)
    manifest = load_project_manifest(path)
    raw = read_catalog_file(match["file"])
    return resolve_template(raw, manifest)


@mcp.tool()
def list_project_skills(manifest_path: str | None = None) -> list[str]:
    """List markdown skill filenames in the project overlay (.skills/ by default)."""
    path = _manifest_path_arg(manifest_path)
    manifest = load_project_manifest(path)
    skills_dir = project_skills_dir(path, manifest)
    if not skills_dir.is_dir():
        return []
    return sorted(p.name for p in skills_dir.glob("*.md") if p.name.lower() != "readme.md")


@mcp.tool()
def get_project_skill(skill_filename: str, manifest_path: str | None = None) -> str:
    """Read a project-local overlay skill (domain-specific checklists)."""
    path = _manifest_path_arg(manifest_path)
    manifest = load_project_manifest(path)
    skills_dir = project_skills_dir(path, manifest)
    skill_path = (skills_dir / skill_filename).resolve()
    if not skill_path.is_file() or skill_path.suffix.lower() != ".md":
        raise FileNotFoundError(f"Project skill not found: {skill_filename}")
    if skills_dir not in skill_path.parents:
        raise ValueError("Skill path must stay within project skills directory.")
    return skill_path.read_text(encoding="utf-8")


@mcp.tool()
def get_project_manifest(manifest_path: str | None = None) -> dict[str, Any]:
    """Return parsed project manifest used for placeholder resolution."""
    return load_project_manifest(_manifest_path_arg(manifest_path))


@mcp.resource("enterprise-sdlc://catalog/manifest")
def catalog_manifest_resource() -> str:
    """Enterprise catalog manifest (agents and skills index)."""
    return json.dumps(load_catalog_manifest(), indent=2)


def _register_catalog_resources() -> None:
    catalog = load_catalog_manifest()

    def _register_agent_resource(agent_id: str) -> None:
        @mcp.resource(f"enterprise-sdlc://agents/{agent_id}")
        def agent_resource() -> str:
            return get_agent(agent_id)

    def _register_skill_resource(skill_id: str) -> None:
        @mcp.resource(f"enterprise-sdlc://skills/{skill_id}")
        def skill_resource() -> str:
            return get_skill(skill_id)

    for agent in catalog.get("agents", []):
        _register_agent_resource(agent["id"])

    for skill in catalog.get("skills", []):
        _register_skill_resource(skill["id"])


_register_catalog_resources()


@mcp.prompt()
def independent_code_review(pr_summary: str = "") -> str:
    """Prompt template to launch an independent Code Reviewer subagent."""
    role = get_agent("code-reviewer")
    checklist = get_skill("pr-code-review")
    return (
        "You are an independent Code Reviewer subagent with fresh context. "
        "Do not assume the implementation is correct.\n\n"
        f"{role}\n\n## Review checklist\n\n{checklist}\n\n"
        f"## PR under review\n\n{pr_summary or '(provide diff and linked issue)'}"
    )


@mcp.prompt()
def architecture_review(scope: str = "") -> str:
    """Prompt template for Solution Architect / Refactor Reviewer structural review."""
    role = get_agent("refactor-reviewer")
    checklist = get_skill("architecture-review")
    return (
        f"{role}\n\n## Architecture review checklist\n\n{checklist}\n\n"
        f"## Scope\n\n{scope or '(describe the change or area under review)'}"
    )
