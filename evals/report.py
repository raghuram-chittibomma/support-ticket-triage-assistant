"""Format and write evaluation reports."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.data_access.loaders import DATA_DIR

from evals.runner import EvalRunResult


def default_report_paths(timestamp: datetime | None = None) -> tuple[Path, Path]:
    ts = timestamp or datetime.now(timezone.utc)
    stamp = ts.strftime("%Y%m%dT%H%M%SZ")
    base = DATA_DIR / "generated" / f"eval-report-{stamp}"
    return base.with_suffix(".json"), base.with_suffix(".md")


def format_markdown_report(run: EvalRunResult) -> str:
    cal = run.confidence_calibration
    rubric = run.rubric_summary
    lines = [
        "# Evaluation Report — Support Ticket Triage Assistant",
        "",
        "## Summary",
        "",
        f"- **Tickets evaluated:** {len(run.scenario_results)}",
        f"- **Category accuracy:** {run.category_accuracy:.1%}",
        f"- **Priority accuracy:** {run.priority_accuracy:.1%}",
        f"- **Missing-fields accuracy:** {run.missing_fields_accuracy:.1%}",
        f"- **Response rubric fully passed:** {rubric['fully_passed']}/{rubric['scenarios']}",
        f"- **Response rubric check pass rate:** {rubric['check_pass_rate']:.1%}",
        "",
        "## Confidence calibration (directional)",
        "",
        f"- Complete tickets (`expected_missing_fields` empty): {cal.complete_ticket_count}",
        f"  - Human-review rate: {cal.complete_human_review_rate:.1%}",
        f"  - Low-confidence rate: {cal.complete_low_confidence_rate:.1%}",
        f"- Incomplete tickets: {cal.incomplete_ticket_count}",
        f"  - Human-review rate: {cal.incomplete_human_review_rate:.1%}",
        f"  - Low-confidence rate: {cal.incomplete_low_confidence_rate:.1%}",
        "",
        "## Mismatches",
        "",
    ]
    if not run.mismatches:
        lines.append("_None — all deterministic and classification fields matched ground truth._")
    else:
        for mismatch in run.mismatches:
            lines.append(
                f"- `{mismatch.ticket_id}` **{mismatch.field}**: "
                f"expected `{mismatch.expected}`, got `{mismatch.actual}`"
            )

    lines.extend(["", "## Response rubric failures", ""])
    rubric_failures = [r for r in run.scenario_results if not r.rubric.all_passed]
    if not rubric_failures:
        lines.append("_All rubric checks passed for every ticket._")
    else:
        for scenario in rubric_failures:
            failed = [c for c in scenario.rubric.checks if not c.passed]
            lines.append(f"- `{scenario.ticket_id}`:")
            for check in failed:
                lines.append(f"  - {check.name}: {check.detail}")

    return "\n".join(lines) + "\n"


def _serialize_run(run: EvalRunResult) -> dict:
    payload = {
        "summary": {
            "ticket_count": len(run.scenario_results),
            "category_accuracy": run.category_accuracy,
            "priority_accuracy": run.priority_accuracy,
            "missing_fields_accuracy": run.missing_fields_accuracy,
            "rubric_summary": run.rubric_summary,
            "confidence_calibration": asdict(run.confidence_calibration),
        },
        "mismatches": [asdict(m) for m in run.mismatches],
        "scenarios": [],
    }
    for scenario in run.scenario_results:
        payload["scenarios"].append(
            {
                "ticket_id": scenario.ticket_id,
                "category_match": scenario.category_match,
                "priority_match": scenario.priority_match,
                "missing_fields_match": scenario.missing_fields_match,
                "predicted_category": scenario.result.category.value,
                "predicted_priority": scenario.result.priority.value,
                "predicted_missing_fields": scenario.result.readiness.missing_fields,
                "confidence_level": scenario.result.confidence_level,
                "human_review_required": scenario.result.human_review_required,
                "rubric": {
                    "passed_count": scenario.rubric.passed_count,
                    "total_count": scenario.rubric.total_count,
                    "checks": [asdict(c) for c in scenario.rubric.checks],
                },
            }
        )
    return payload


def write_report(run: EvalRunResult, output_base: Path | None = None) -> tuple[Path, Path]:
    """Write JSON and Markdown reports under data/generated/. Returns both paths."""
    json_path, md_path = default_report_paths() if output_base is None else (
        output_base.with_suffix(".json"),
        output_base.with_suffix(".md"),
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(_serialize_run(run), indent=2), encoding="utf-8")
    md_path.write_text(format_markdown_report(run), encoding="utf-8")
    return json_path, md_path
