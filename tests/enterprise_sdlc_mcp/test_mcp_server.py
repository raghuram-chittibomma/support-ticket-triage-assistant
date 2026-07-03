"""Tests for enterprise SDLC MCP resolver and tools."""

from pathlib import Path

import pytest

from enterprise_sdlc_mcp.server.resolver import (
    load_catalog_manifest,
    load_project_manifest,
    read_catalog_file,
    resolve_template,
)
from enterprise_sdlc_mcp.server.server import (
    get_agent,
    get_skill,
    list_agents,
    list_project_skills,
    list_skills,
)


@pytest.fixture
def manifest_path() -> Path:
    path = Path("sdlc.project.yaml")
    assert path.is_file()
    return path.resolve()


def test_catalog_lists_agents_and_skills() -> None:
    catalog = load_catalog_manifest()
    assert len(catalog["agents"]) == 8
    assert len(catalog["skills"]) == 13


def test_resolve_template_substitutes_project_paths(manifest_path: Path) -> None:
    manifest = load_project_manifest(manifest_path)
    raw = read_catalog_file("agents/code-reviewer.md")
    resolved = resolve_template(raw, manifest)
    assert "{{project." not in resolved
    assert "src/" in resolved
    assert "docs/01_architecture/ARCHITECTURE.md" in resolved


def test_get_agent_resolves_for_project(manifest_path: Path) -> None:
    content = get_agent("code-reviewer", str(manifest_path))
    assert "Code Reviewer" in content
    assert "src/" in content


def test_get_skill_resolves_for_project(manifest_path: Path) -> None:
    content = get_skill("pr-code-review", str(manifest_path))
    assert "Closes #<n>" in content


def test_list_tools_return_entries() -> None:
    assert len(list_agents()) == 8
    assert len(list_skills()) == 13


def test_list_project_skills_finds_domain_overlay(manifest_path: Path) -> None:
    names = list_project_skills(str(manifest_path))
    assert "hifi-audio-support-taxonomy-design.md" in names
    assert "architecture-review.md" not in names
