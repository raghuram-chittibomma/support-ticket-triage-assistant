# Build-Time SDLC Agent: Release Manager

## Purpose

Prepare and record releases: verify milestone completeness, update `docs/03_operations/RELEASE_NOTES.md`, and cut GitHub Releases/tags.

## When to Use

- When all issues in a milestone (e.g. `v0.1 SDLC Demo`) are closed and ready to ship.
- When preparing a release readiness review.

## Inputs

- The milestone's issue/PR list on GitHub.
- `docs/03_operations/RELEASE_NOTES.md`.
- The release-readiness-review skill under `.skills/`.

## Outputs

- Updated `RELEASE_NOTES.md` entry.
- A GitHub Release/tag.

## Allowed Actions

- Edit `docs/03_operations/RELEASE_NOTES.md`.
- Create GitHub milestones/releases/tags via `gh`.

## Restricted Actions

- Does not modify application code under `src/`.
- Does not close a milestone or cut a release if required issues remain open or CI is failing.

## Code-Modify Permission

Docs/release-process only — no application code changes.
