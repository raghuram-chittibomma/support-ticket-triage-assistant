# Evaluation Strategy — Support Ticket Triage Assistant

## Purpose

Measure the quality of the AI-dependent parts of the pipeline (classification, response drafting) in a way that unit tests cannot — where "correct" is not a single deterministic value but a judgment of adequacy.

## Evaluation Dataset

A curated set of synthetic tickets under `data/sample/tickets.json`, each with ground-truth fields: `expected_category`, `expected_priority`, `expected_missing_fields`. The set is designed to cover every category in the taxonomy, a mix of complete and incomplete tickets, and a mix of priority levels, using the synthetic NorthPeak Audioworks product catalog.

## Evaluation Dimensions

- **Classification accuracy:** predicted `category` matches `expected_category`.
- **Priority accuracy:** predicted `priority` matches `expected_priority` (deterministic — should be at or near 100%; regressions here indicate a rule bug, not a model limitation).
- **Readiness/missing-info accuracy:** predicted missing fields match `expected_missing_fields` (deterministic).
- **Response quality (qualitative spot check):** a sample of drafted responses reviewed against a short rubric — grounded in a cited reference where applicable, addresses the customer's stated issue, professional tone, no fabricated policy claims.
- **Confidence calibration (directional check):** tickets expected to be ambiguous or incomplete should generally receive lower confidence / a human-review flag; this is checked as a trend, not an exact threshold, in v0.1.

## Runner

`evals/` contains an evaluation scenario runner that loads the ticket dataset, runs each ticket through the pipeline, compares deterministic fields exactly, and produces a summary report (accuracy per dimension, list of mismatches for manual review). Ephemeral output goes to `data/generated/` (gitignored). **Release snapshots** are recorded under `evals/baselines/` via `python -m evals.record_baseline` — see `evals/baselines/README.md` and `QUALITY_BAR.md`.

## When Evaluations Run

Run manually during development of classification/drafting-related slices. **Fixture baselines** (`--mode fixture`) run in CI and require no API key. **Live baselines** (`--mode live`) are optional at release and compared to `evals/baselines/QUALITY_BAR.md`.

## Relationship to Tests

Unit/integration tests (see `TEST_STRATEGY.md`) are the blocking quality gate for deterministic logic. Evaluations are the primary quality signal for LLM-backed behavior and are reviewed by the Main Orchestrator (optionally assisted by the Test/Eval Designer Agent) before considering a classification/drafting-related slice complete.
