"""Deterministic confidence scoring. See docs/01_architecture/DATA_MODEL.md Section 12.

Resolves the open question in docs/00_project/AI_ORCHESTRATOR_BRIEF.md Section 16 (the
confidence-weighting formula). No LLM call — a deterministic combination of three
already-computed upstream signals: classifier confidence, ticket readiness, and retrieval
match strength (approximated here as "did the retriever return anything").
"""

from typing import Literal

from src.schemas import ReadinessResult, Reference

ConfidenceLevel = Literal["high", "medium", "low"]

NOT_READY_PENALTY = 0.25
HAS_REFERENCES_BONUS = 0.05

HIGH_THRESHOLD = 0.75
MEDIUM_THRESHOLD = 0.5


def score_confidence(
    category_confidence: float,
    readiness: ReadinessResult,
    references: list[Reference],
) -> tuple[ConfidenceLevel, str]:
    """Return (confidence_level, reason) for the given upstream signals.

    See DATA_MODEL.md Section 12 for the full rationale behind the weights/thresholds below.
    """
    score = category_confidence
    reasons = [f"classifier confidence {category_confidence:.2f}"]

    if not readiness.is_ready:
        score -= NOT_READY_PENALTY
        reasons.append(f"-{NOT_READY_PENALTY:.2f} ticket is missing required information")

    if references:
        score += HAS_REFERENCES_BONUS
        reasons.append(f"+{HAS_REFERENCES_BONUS:.2f} relevant knowledge-base reference(s) found")

    # Round before clamping/thresholding: all weights (0.25, 0.05) and thresholds (0.75, 0.5)
    # are two-decimal values, but IEEE-754 float arithmetic can otherwise leave a
    # mathematically-exact threshold value (e.g. 0.7 - 0.25 + 0.05 == 0.49999999999999994)
    # a hair below the boundary, silently flipping the bucket the docs promise.
    score = round(max(0.0, min(1.0, score)), 2)

    if score >= HIGH_THRESHOLD:
        level: ConfidenceLevel = "high"
    elif score >= MEDIUM_THRESHOLD:
        level = "medium"
    else:
        level = "low"

    reason = f"Combined confidence score {score:.2f} ({'; '.join(reasons)})."
    return level, reason
