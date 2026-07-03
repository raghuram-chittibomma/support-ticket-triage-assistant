from src.schemas import ReadinessResult, Reference
from src.services.confidence import score_confidence


def _reference() -> Reference:
    return Reference(doc_id="KB-WIFI-004", title="Wi-Fi reconnect guide", excerpt="...")


class TestScoreConfidenceLevels:
    def test_high_confidence_when_ready_and_grounded(self):
        readiness = ReadinessResult(is_ready=True, missing_fields=[])

        level, reason = score_confidence(0.9, readiness, [_reference()])

        assert level == "high"
        assert isinstance(reason, str) and reason

    def test_medium_confidence_when_moderate_classifier_confidence(self):
        readiness = ReadinessResult(is_ready=True, missing_fields=[])

        level, _ = score_confidence(0.65, readiness, [])

        assert level == "medium"

    def test_low_confidence_when_not_ready_and_low_classifier_confidence(self):
        readiness = ReadinessResult(is_ready=False, missing_fields=["firmware_version"])

        level, reason = score_confidence(0.4, readiness, [])

        assert level == "low"
        assert "missing required information" in reason


class TestScoreConfidenceBehavior:
    def test_not_ready_pushes_a_high_classifier_confidence_down(self):
        ready = ReadinessResult(is_ready=True, missing_fields=[])
        not_ready = ReadinessResult(is_ready=False, missing_fields=["firmware_version"])

        ready_level, _ = score_confidence(0.9, ready, [])
        not_ready_level, _ = score_confidence(0.9, not_ready, [])

        assert ready_level == "high"
        assert not_ready_level != "high"

    def test_empty_references_is_neutral_not_penalized(self):
        readiness = ReadinessResult(is_ready=True, missing_fields=[])

        with_refs, _ = score_confidence(0.85, readiness, [_reference()])
        without_refs, _ = score_confidence(0.85, readiness, [])

        # Both remain "high" — an empty reference list must not push a well-classified,
        # ready ticket out of "high" just because its category has no KB coverage.
        assert with_refs == "high"
        assert without_refs == "high"

    def test_score_is_clamped_to_valid_range(self):
        readiness = ReadinessResult(is_ready=False, missing_fields=["x"])

        level, reason = score_confidence(0.05, readiness, [])

        assert level == "low"
        assert "0.00" in reason  # clamped, never negative

    def test_deterministic(self):
        readiness = ReadinessResult(is_ready=True, missing_fields=[])

        first = score_confidence(0.8, readiness, [_reference()])
        second = score_confidence(0.8, readiness, [_reference()])

        assert first == second


class TestScoreConfidenceBoundaries:
    """Regression tests for a floating-point drift bug found in code review: a score that is
    mathematically exactly at a threshold (e.g. 0.7 - 0.25 + 0.05 == 0.49999999999999994 in
    raw IEEE-754 arithmetic) must still land in the documented bucket, not the one below it."""

    def test_score_exactly_at_medium_threshold_is_medium_not_low(self):
        not_ready = ReadinessResult(is_ready=False, missing_fields=["x"])

        # 0.7 - 0.25 (not ready) + 0.05 (has references) == 0.5 mathematically.
        level, reason = score_confidence(0.7, not_ready, [_reference()])

        assert level == "medium"
        assert "0.50" in reason

    def test_score_exactly_at_high_threshold_is_high_not_medium(self):
        not_ready = ReadinessResult(is_ready=False, missing_fields=["x"])

        # 0.95 - 0.25 (not ready) + 0.05 (has references) == 0.75 mathematically.
        level, _ = score_confidence(0.95, not_ready, [_reference()])

        assert level == "high"

    def test_out_of_range_category_confidence_is_clamped(self):
        readiness = ReadinessResult(is_ready=True, missing_fields=[])

        high_level, _ = score_confidence(1.7, readiness, [])
        low_level, _ = score_confidence(-0.3, readiness, [])

        assert high_level == "high"
        assert low_level == "low"
