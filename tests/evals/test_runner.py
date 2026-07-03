"""Tests for evals/ — use a faked LLMClient; no network calls in the default suite."""

from __future__ import annotations

import json
import os

import pytest

from evals.fixture_llm import PerScenarioScriptedLLM
from evals.loader import load_eval_scenarios
from evals.report import format_markdown_report, write_report
from evals.rubric import evaluate_response_rubric
from evals.runner import run_eval_suite
from src.llm import OpenAILLMClient
from src.retrieval import KeywordKBRetriever
from src.schemas import Category, Priority, ReadinessResult, Reference, TriageResult
from src.workflows.triage_pipeline import run_triage_pipeline


class ScriptedLLMClient:
    def __init__(self, expected_category: Category):
        self.expected_category = expected_category

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        if "Choose exactly one category" in system_prompt:
            return json.dumps(
                {
                    "category": self.expected_category.value,
                    "explanation": f"Matches {self.expected_category.value}.",
                }
            )
        return json.dumps(
            {
                "likely_issue": "The customer is experiencing the issue described in the ticket.",
                "suggested_next_action": "Review the ticket and respond with tailored guidance.",
                "suggested_response": (
                    "Thanks for reaching out — we can help with your speaker issue."
                ),
            }
        )


class WrongCategoryLLMClient:
    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        if "Choose exactly one category" in system_prompt:
            return json.dumps(
                {
                    "category": Category.GENERAL_QUESTION.value,
                    "explanation": "Wrong on purpose.",
                }
            )
        return json.dumps(
            {
                "likely_issue": "General question.",
                "suggested_next_action": "Respond generally.",
                "suggested_response": "Thanks for your question about your speaker issue.",
            }
        )


@pytest.fixture
def first_scenario():
    return load_eval_scenarios()[0]


class TestLoadEvalScenarios:
    def test_loads_all_sample_tickets_with_ground_truth(self):
        scenarios = load_eval_scenarios()
        assert len(scenarios) == 25
        assert {s.expected_category for s in scenarios}
        assert scenarios[0].ticket_id == "TCK-0001"


class TestRunEvalSuite:
    def test_perfect_scores_with_scripted_llm(self):
        scenarios = load_eval_scenarios()[:3]
        run = run_eval_suite(PerScenarioScriptedLLM(), scenarios=scenarios)

        assert run.category_accuracy == 1.0
        assert run.priority_accuracy == 1.0
        assert run.missing_fields_accuracy == 1.0
        assert run.mismatches == []

    def test_detects_category_mismatch(self, first_scenario):
        run = run_eval_suite(WrongCategoryLLMClient(), scenarios=[first_scenario])
        assert run.category_accuracy == 0.0
        assert any(m.field == "category" for m in run.mismatches)

    def test_report_writes_json_and_markdown(self, tmp_path):
        scenarios = load_eval_scenarios()[:2]
        run = run_eval_suite(PerScenarioScriptedLLM(), scenarios=scenarios)
        json_path, md_path = write_report(run, tmp_path / "eval-test")
        assert json_path.is_file()
        assert md_path.is_file()
        assert "Category accuracy" in md_path.read_text(encoding="utf-8")


class TestResponseRubric:
    def test_passes_well_formed_response(self, first_scenario):
        result = run_triage_pipeline(
            first_scenario.ticket,
            llm_client=ScriptedLLMClient(first_scenario.expected_category),
            retriever=KeywordKBRetriever(),
        )
        rubric = evaluate_response_rubric(first_scenario.ticket_id, first_scenario.ticket.subject, result)
        assert rubric.all_passed

    def test_fails_empty_response(self, first_scenario):
        result = TriageResult(
            category=first_scenario.expected_category,
            category_confidence=0.9,
            category_explanation="ok",
            priority=first_scenario.expected_priority,
            priority_reason="ok",
            readiness=ReadinessResult(is_ready=True, missing_fields=[]),
            likely_issue="",
            suggested_next_action="act",
            suggested_response="",
            references=[],
            confidence_level="high",
            human_review_required=False,
        )
        rubric = evaluate_response_rubric(first_scenario.ticket_id, first_scenario.ticket.subject, result)
        assert not rubric.all_passed
        assert any(c.name == "non_empty_response" and not c.passed for c in rubric.checks)

    def test_fails_fabricated_citation(self, first_scenario):
        result = TriageResult(
            category=first_scenario.expected_category,
            category_confidence=0.9,
            category_explanation="ok",
            priority=first_scenario.expected_priority,
            priority_reason="ok",
            readiness=ReadinessResult(is_ready=True, missing_fields=[]),
            likely_issue="Wi-Fi issue likely.",
            suggested_next_action="act",
            suggested_response="See (KB-FAKE-999) for steps on your speaker issue.",
            references=[Reference(doc_id="KB-WIFI-004", title="Wi-Fi help", excerpt="excerpt")],
            confidence_level="high",
            human_review_required=False,
        )
        rubric = evaluate_response_rubric(first_scenario.ticket_id, first_scenario.ticket.subject, result)
        assert any(c.name == "citation_integrity" and not c.passed for c in rubric.checks)


@pytest.mark.llm
def test_live_eval_smoke():
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    scenarios = load_eval_scenarios()[:1]
    run = run_eval_suite(OpenAILLMClient(), scenarios=scenarios)
    assert len(run.scenario_results) == 1
    assert format_markdown_report(run)
