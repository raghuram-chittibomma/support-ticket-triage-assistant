"""Response quality rubric for evaluation spot checks.

See evals/RUBRIC.md for the human-readable rubric this module implements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.schemas import TriageResult

_DOC_ID_PATTERN = re.compile(r"\bKB-[A-Za-z0-9-]+\b", re.IGNORECASE)
_PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|\[INSERT|\[insert|lorem ipsum)\b", re.IGNORECASE)
_PROFANITY_PATTERN = re.compile(r"\b(damn|hell\b|shit|fuck)\b", re.IGNORECASE)


@dataclass(frozen=True)
class RubricCheck:
    name: str
    passed: bool
    detail: str


@dataclass
class ResponseRubricResult:
    """Heuristic rubric score for one drafted response."""

    ticket_id: str
    checks: list[RubricCheck] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def total_count(self) -> int:
        return len(self.checks)

    @property
    def all_passed(self) -> bool:
        return self.total_count > 0 and self.passed_count == self.total_count


def _significant_words(text: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[A-Za-z]{4,}", text)}


def _addresses_subject(subject: str, response: str) -> bool:
    response_lower = response.lower()
    for word in _significant_words(subject):
        if word in response_lower:
            return True
        if len(word) >= 5 and word[:5] in response_lower:
            return True
    return False


def evaluate_response_rubric(ticket_id: str, subject: str, result: TriageResult) -> ResponseRubricResult:
    """Apply the v0.1 response-quality rubric to one pipeline result."""
    checks: list[RubricCheck] = []
    response = result.suggested_response.strip()
    likely_issue = result.likely_issue.strip()

    checks.append(
        RubricCheck(
            name="non_empty_response",
            passed=len(response) >= 20,
            detail="suggested_response has at least 20 characters",
        )
    )
    checks.append(
        RubricCheck(
            name="likely_issue_present",
            passed=len(likely_issue) >= 10,
            detail="likely_issue is present and substantive",
        )
    )
    checks.append(
        RubricCheck(
            name="no_placeholders",
            passed=_PLACEHOLDER_PATTERN.search(response) is None,
            detail="no TODO/TBD/placeholder tokens in suggested_response",
        )
    )
    checks.append(
        RubricCheck(
            name="professional_tone",
            passed=_PROFANITY_PATTERN.search(response) is None,
            detail="no obvious profanity in suggested_response",
        )
    )

    checks.append(
        RubricCheck(
            name="addresses_stated_issue",
            passed=_addresses_subject(subject, response),
            detail="ticket subject vocabulary appears in suggested_response",
        )
    )

    cited_ids = {match.group(0).upper() for match in _DOC_ID_PATTERN.finditer(response)}
    allowed_ids = {ref.doc_id.upper() for ref in result.references}
    if cited_ids:
        checks.append(
            RubricCheck(
                name="citation_integrity",
                passed=cited_ids.issubset(allowed_ids),
                detail="every cited doc_id in suggested_response was retrieved",
            )
        )

    return ResponseRubricResult(ticket_id=ticket_id, checks=checks)


def summarize_rubric_results(results: list[ResponseRubricResult]) -> dict[str, float | int]:
    """Aggregate rubric pass rates across scenarios."""
    if not results:
        return {"scenarios": 0, "fully_passed": 0, "check_pass_rate": 0.0}
    total_checks = sum(r.total_count for r in results)
    passed_checks = sum(r.passed_count for r in results)
    return {
        "scenarios": len(results),
        "fully_passed": sum(1 for r in results if r.all_passed),
        "check_pass_rate": passed_checks / total_checks if total_checks else 0.0,
    }
