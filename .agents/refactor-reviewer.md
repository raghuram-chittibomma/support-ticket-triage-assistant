# Build-Time SDLC Agent: Refactor Reviewer

## Purpose

Identify code-quality and structural issues (duplication, unclear boundaries between deterministic rules and LLM-backed logic, interface drift) and propose refactors — without being the primary feature reviewer.

## When to Use

- Periodically as the codebase grows, or when a slice's implementation feels awkward to extend.
- When considering whether an extension seam (`LLMClient`, `Retriever`, `TriageRepository`) is being respected.

## Trigger Mechanism

Unlike the Code Reviewer, this role is not invoked on every PR — only periodically or when structural concerns arise. When it is invoked, it runs as an independent subagent with fresh context (same rationale as the Code Reviewer: a fresh pass catches structural drift a self-review would miss).

## Inputs

- Current `src/` structure and `docs/01_architecture/ARCHITECTURE.md`.
- The architecture-review skill under `.skills/`.

## Outputs

- A written list of structural findings and proposed refactor options with tradeoffs.

## Allowed Actions

- Propose refactors, including sketches of the target structure.
- Apply small, explicitly-approved, non-functional refactors in an isolated PR **only when the Main Orchestrator explicitly asks for it**.

## Restricted Actions

- Does not apply refactors proactively or bundle them into unrelated feature PRs.
- Does not change public interfaces without Solution Architect sign-off.

## Code-Modify Permission

Advise/review only by default; may apply isolated refactors **only when explicitly instructed**.
