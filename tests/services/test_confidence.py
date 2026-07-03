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
