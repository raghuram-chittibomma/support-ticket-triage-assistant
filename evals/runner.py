"""Evaluation scenario runner."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.llm import LLMClient
from src.retrieval import KeywordKBRetriever, Retriever
from src.schemas import Category, Priority, TriageResult
from src.workflows.triage_pipeline import run_triage_pipeline

from evals.loader import EvalScenario, load_eval_scenarios
from evals.rubric import ResponseRubricResult, evaluate_response_rubric, summarize_rubric_results


@dataclass(frozen=True)
class FieldMismatch:
    ticket_id: str
    field: str
    expected: str
    actual: str


@dataclass
class ScenarioEvalResult:
    ticket_id: str
    expected_category: Category
    expected_priority: Priority
    expected_missing_fields: list[str]
    result: TriageResult
    category_match: bool
    priority_match: bool
    missing_fields_match: bool
    rubric: ResponseRubricResult
    mismatches: list[FieldMismatch] = field(default_factory=list)


@dataclass
class ConfidenceCalibrationSummary:
    """Directional trend: incomplete tickets vs complete tickets."""

    complete_ticket_count: int
    incomplete_ticket_count: int
    complete_human_review_rate: float
    incomplete_human_review_rate: float
    complete_low_confidence_rate: float
    incomplete_low_confidence_rate: float


@dataclass
class EvalRunResult:
    scenario_results: list[ScenarioEvalResult]
    category_accuracy: float
    priority_accuracy: float
    missing_fields_accuracy: float
    mismatches: list[FieldMismatch]
    rubric_summary: dict[str, float | int]
    confidence_calibration: ConfidenceCalibrationSummary


def _collect_mismatches(scenario: EvalScenario, result: TriageResult) -> tuple[bool, bool, bool, list[FieldMismatch]]:
    mismatches: list[FieldMismatch] = []
    category_match = result.category == scenario.expected_category
    priority_match = result.priority == scenario.expected_priority
    predicted_missing = sorted(result.readiness.missing_fields)
    expected_missing = sorted(scenario.expected_missing_fields)
    missing_fields_match = predicted_missing == expected_missing

    if not category_match:
        mismatches.append(
            FieldMismatch(
                ticket_id=scenario.ticket_id,
                field="category",
                expected=scenario.expected_category.value,
                actual=result.category.value,
            )
        )
    if not priority_match:
        mismatches.append(
            FieldMismatch(
                ticket_id=scenario.ticket_id,
                field="priority",
                expected=scenario.expected_priority.value,
                actual=result.priority.value,
            )
        )
    if not missing_fields_match:
        mismatches.append(
            FieldMismatch(
                ticket_id=scenario.ticket_id,
                field="missing_fields",
                expected=str(expected_missing),
                actual=str(predicted_missing),
            )
        )
    return category_match, priority_match, missing_fields_match, mismatches


def _accuracy(matches: list[bool]) -> float:
    return sum(matches) / len(matches) if matches else 0.0


def _human_review_rate(results: list[ScenarioEvalResult], *, incomplete: bool) -> float:
    subset = [
        r
        for r in results
        if bool(r.expected_missing_fields) is incomplete
    ]
    if not subset:
        return 0.0
    return sum(1 for r in subset if r.result.human_review_required) / len(subset)


def _low_confidence_rate(results: list[ScenarioEvalResult], *, incomplete: bool) -> float:
    subset = [
        r
        for r in results
        if bool(r.expected_missing_fields) is incomplete
    ]
    if not subset:
        return 0.0
    return sum(1 for r in subset if r.result.confidence_level == "low") / len(subset)


def run_eval_suite(
    llm_client: LLMClient,
    *,
    retriever: Retriever | None = None,
    scenarios: list[EvalScenario] | None = None,
) -> EvalRunResult:
    """Run every scenario through the triage pipeline and score against ground truth."""
    scenarios = scenarios if scenarios is not None else load_eval_scenarios()
    retriever = retriever if retriever is not None else KeywordKBRetriever()

    scenario_results: list[ScenarioEvalResult] = []
    all_mismatches: list[FieldMismatch] = []

    for scenario in scenarios:
        result = run_triage_pipeline(scenario.ticket, llm_client=llm_client, retriever=retriever)
        category_match, priority_match, missing_fields_match, mismatches = _collect_mismatches(
            scenario, result
        )
        rubric = evaluate_response_rubric(scenario.ticket_id, scenario.ticket.subject, result)
        all_mismatches.extend(mismatches)
        scenario_results.append(
            ScenarioEvalResult(
                ticket_id=scenario.ticket_id,
                expected_category=scenario.expected_category,
                expected_priority=scenario.expected_priority,
                expected_missing_fields=scenario.expected_missing_fields,
                result=result,
                category_match=category_match,
                priority_match=priority_match,
                missing_fields_match=missing_fields_match,
                rubric=rubric,
                mismatches=mismatches,
            )
        )

    complete_count = sum(1 for r in scenario_results if not r.expected_missing_fields)
    incomplete_count = len(scenario_results) - complete_count

    return EvalRunResult(
        scenario_results=scenario_results,
        category_accuracy=_accuracy([r.category_match for r in scenario_results]),
        priority_accuracy=_accuracy([r.priority_match for r in scenario_results]),
        missing_fields_accuracy=_accuracy([r.missing_fields_match for r in scenario_results]),
        mismatches=all_mismatches,
        rubric_summary=summarize_rubric_results([r.rubric for r in scenario_results]),
        confidence_calibration=ConfidenceCalibrationSummary(
            complete_ticket_count=complete_count,
            incomplete_ticket_count=incomplete_count,
            complete_human_review_rate=_human_review_rate(scenario_results, incomplete=False),
            incomplete_human_review_rate=_human_review_rate(scenario_results, incomplete=True),
            complete_low_confidence_rate=_low_confidence_rate(scenario_results, incomplete=False),
            incomplete_low_confidence_rate=_low_confidence_rate(scenario_results, incomplete=True),
        ),
    )
