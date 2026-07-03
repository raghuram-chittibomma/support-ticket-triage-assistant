# Portfolio tour — how to read this repo (5 stops)

**Audience:** Recruiters, PMs, and engineers evaluating *how* this project was delivered — not only the triage demo.

**Time:** ~10 minutes without cloning; ~20 if you skim one PR and run pytest.

The demo app (NorthPeak Audioworks ticket triage) is the **proof the process ran**. The **portfolio artifact** is the GitHub-first, agent-assisted SDLC documented here and in Issues/PRs.

---

## Stop 1 — Delivery thesis (2 min)

Read: [`DELIVERY_RECORD.md`](DELIVERY_RECORD.md)

You should leave with:

- Two programs in one repo (triage product vs Enterprise SDLC MCP)
- Timeline and metrics from real git/GitHub data (12 merged PRs, v0.1.0 in two calendar days)
- Quality gates: pytest, fixture eval baseline, independent Code Reviewer

---

## Stop 2 — Backlog shape (2 min)

Read: [`PRODUCT_BRIEF.md`](PRODUCT_BRIEF.md) § Traceability to Backlog

You should leave with:

- FR1–FR8 map to **user stories**, not architecture components
- Enabler work (#29) separated from user-visible stories
- GitHub Issues as source of truth — local docs only link, not duplicate status

Optional: browse [closed issues](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/issues?q=is%3Aissue+is%3Aclosed) for the `v0.1 SDLC Demo` milestone.

---

## Stop 3 — One slice + review finding (5 min)

Pick **one** of these merged PRs (smallest → richest):

| PR | Why open it |
|----|-------------|
| [#38](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/38) | First application slice — data, schema, readiness |
| [#43](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/43) | Reviewer caught IEEE-754 float threshold bug before merge |
| [#51](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/51) | Separate program: Enterprise SDLC MCP catalog |

Then read the matching section in [`RELEASE_NOTES.md`](../03_operations/RELEASE_NOTES.md) — it records **independent Code Reviewer outcomes** (including blocking bugs), not only what shipped.

---

## Stop 4 — Build-time agents (2 min)

Read: [`AGENTS.md`](../../AGENTS.md) (short) → skim [`ENTERPRISE_SDLC_MCP.md`](../01_architecture/ENTERPRISE_SDLC_MCP.md) intro

You should leave with:

- Build-time SDLC roles (MCP) ≠ runtime pipeline components (`src/`)
- Pre-merge review path: fresh-context Code Reviewer via MCP ([#53](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/pull/53) codified this)

Catalog lives under [`enterprise_sdlc_mcp/`](../../enterprise_sdlc_mcp/).

---

## Stop 5 — Quality gates in CI (2 min)

Skim:

- [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — `pytest -m "not llm"` on every PR
- [`evals/baselines/v0.1.0/fixture-baseline.json`](../../evals/baselines/v0.1.0/fixture-baseline.json) — pinned reproducible eval snapshot
- [`evals/baselines/QUALITY_BAR.md`](../../evals/baselines/QUALITY_BAR.md) — acceptance thresholds for live LLM runs

Optional clone check:

```bash
pip install -e ".[dev]"
pytest -m "not llm"
```

---

## Demo vehicle (last, not first)

If you want to see the product: [`RUNBOOK.md`](../03_operations/RUNBOOK.md) → `python -m src.ui` (requires `OPENAI_API_KEY`).

A short screen recording linked from the [v0.1.0 release](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/releases/tag/v0.1.0) is the intended “30-second proof” — optional owner artifact.

---

## Share this path

When sending the repo to someone, paste:

1. [README — Delivery](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant#delivery-portfolio-focus)
2. This tour: `docs/00_project/PORTFOLIO_TOUR.md`
3. One PR from Stop 3
4. Release: [v0.1.0](https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/releases/tag/v0.1.0)

**Elevator line:** *AI coding agents as a delivery team — GitHub-owned backlog, thin slices, independent agent review, tests/evals, and CI — shipping a small LLM demo end-to-end; the repo is the case study, the triage app is the proof.*
