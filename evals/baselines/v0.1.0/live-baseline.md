<!-- baseline-mode: live -->
<!-- recorded-at: 2026-07-03T19:25:21Z -->
<!-- tag: v0.1.0 -->
<!-- openai-model: gpt-4o-mini -->

# Evaluation Report — Support Ticket Triage Assistant

## Summary

- **Tickets evaluated:** 25
- **Category accuracy:** 100.0%
- **Priority accuracy:** 100.0%
- **Missing-fields accuracy:** 100.0%
- **Response rubric fully passed:** 24/25
- **Response rubric check pass rate:** 99.2%

## Confidence calibration (directional)

- Complete tickets (`expected_missing_fields` empty): 13
  - Human-review rate: 7.7%
  - Low-confidence rate: 0.0%
- Incomplete tickets: 12
  - Human-review rate: 100.0%
  - Low-confidence rate: 25.0%

## Mismatches

_None — all deterministic and classification fields matched ground truth._

## Response rubric failures

- `TCK-0018`:
  - addresses_stated_issue: ticket subject vocabulary appears in suggested_response
