"""Resolve {{project.*}} placeholders from a project manifest."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MANIFEST_ENV = "SDLC_PROJECT_MANIFEST"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def catalog_root() -> Path:
    return Path(__file__).resolve().parent.parent / "catalog"


def default_manifest_path() -> Path | None:
    env_path = os.environ.get(DEFAULT_MANIFEST_ENV)
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = repo_root() / path
        return path.resolve()
    for candidate in (repo_root() / "sdlc.project.yaml", Path.cwd() / "sdlc.project.yaml"):
        if candidate.is_file():
            return candidate.resolve()
    return None


def load_project_manifest(manifest_path: Path | None = None) -> dict[str, Any]:
    path = manifest_path or default_manifest_path()
    if path is None or not path.is_file():
        raise FileNotFoundError(
            "Project manifest not found. Set SDLC_PROJECT_MANIFEST or add sdlc.project.yaml at repo root."
        )
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Project manifest must be a YAML mapping.")
    return data


def manifest_repo_root(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    root = manifest.get("repo_root")
    if root and str(root) != ".":
        path = Path(str(root))
        return path.resolve() if path.is_absolute() else (manifest_path.parent / path).resolve()
    return manifest_path.parent.resolve()


def project_skills_dir(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    paths = manifest.get("paths") or {}
    skills_rel = paths.get("project_skills", ".skills/")
    return (manifest_repo_root(manifest_path, manifest) / skills_rel).resolve()


def _flatten(prefix: str, value: Any, out: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _flatten(f"{prefix}.{key}" if prefix else key, nested, out)
    elif isinstance(value, list):
        out[prefix] = ", ".join(str(item) for item in value)
    else:
        out[prefix] = str(value)


def flatten_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    flat: dict[str, str] = {}
    _flatten("project", manifest, flat)
    return flat


def resolve_template(text: str, manifest: dict[str, Any]) -> str:
    flat = flatten_manifest(manifest)
    resolved = text
    for key, value in flat.items():
        resolved = resolved.replace(f"{{{{{key}}}}}", value)
    return resolved


def read_catalog_file(relative_path: str) -> str:
    path = catalog_root() / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Catalog file not found: {relative_path}")
    return path.read_text(encoding="utf-8")


def load_catalog_manifest() -> dict[str, Any]:
    manifest_path = catalog_root() / "manifest.yaml"
    with manifest_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Catalog manifest must be a YAML mapping.")
    return data
