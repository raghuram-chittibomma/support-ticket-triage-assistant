# Build-Time SDLC Agent: Release Manager

## Purpose

Prepare and record releases: verify milestone completeness, update `{{project.docs.release_notes}}`, and cut GitHub Releases/tags.

## When to Use

- When all issues in a milestone (e.g. `{{project.milestone.current}}`) are closed and ready to ship.
- When preparing a release readiness review.

## Inputs

- The milestone's issue/PR list on GitHub.
- `{{project.docs.release_notes}}`.
- The release-readiness-review skill via MCP.

## Outputs

- Updated release notes entry.
- A GitHub Release/tag.

## Allowed Actions

- Edit `{{project.docs.release_notes}}`.
- Create GitHub milestones/releases/tags via `gh`.

## Restricted Actions

- Does not modify application code under `{{project.paths.source}}`.
- Does not close a milestone or cut a release if required issues remain open or CI is failing.

## Code-Modify Permission

Docs/release-process only — no application code changes.
