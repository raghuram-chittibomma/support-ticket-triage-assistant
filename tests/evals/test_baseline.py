"""Tests that committed fixture baselines match the current runner output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals.fixture_llm import PerScenarioScriptedLLM
from evals.loader import load_eval_scenarios
from evals.runner import run_eval_suite

_FIXTURE_BASELINE = (
    Path(__file__).resolve().parents[2] / "evals" / "baselines" / "v0.1.0" / "fixture-baseline.json"
)


class TestCommittedFixtureBaseline:
    def test_v0_1_0_fixture_baseline_file_exists(self):
        assert _FIXTURE_BASELINE.is_file(), (
            "Missing evals/baselines/v0.1.0/fixture-baseline.json — "
            "run: python -m evals.record_baseline --mode fixture --tag v0.1.0"
        )

    def test_fixture_run_matches_committed_summary(self):
        committed = json.loads(_FIXTURE_BASELINE.read_text(encoding="utf-8"))
        summary = committed["summary"]
        run = run_eval_suite(PerScenarioScriptedLLM(), scenarios=load_eval_scenarios())
        assert run.category_accuracy == summary["category_accuracy"]
        assert run.priority_accuracy == summary["priority_accuracy"]
        assert run.missing_fields_accuracy == summary["missing_fields_accuracy"]
        assert len(run.mismatches) == len(committed["mismatches"])
