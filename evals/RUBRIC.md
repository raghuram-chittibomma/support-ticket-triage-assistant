# Response Quality Rubric (v0.1)

Applied by `evals/rubric.py` to every drafted response in an evaluation run. This is a **heuristic spot-check**, not a substitute for human review of LLM phrasing.

## Checks

| Check | Pass criteria |
|-------|----------------|
| **non_empty_response** | `suggested_response` is at least 20 characters |
| **likely_issue_present** | `likely_issue` is at least 10 characters |
| **no_placeholders** | No TODO/TBD/`[INSERT`/lorem ipsum tokens in the draft |
| **professional_tone** | No obvious profanity in the draft |
| **addresses_stated_issue** | At least one significant word (4+ letters) from the ticket subject appears in `suggested_response` |
| **citation_integrity** | Every `KB-*` doc_id cited in the response was actually retrieved |

When references are retrieved but not explicitly cited, the response may still pass if it is substantive and addresses the issue — human review remains the backstop for grounding quality.

## How to interpret results

- **Deterministic dimensions** (priority, missing fields) should be at or near 100%. Regressions indicate rule bugs.
- **Classification accuracy** depends on the LLM and is the primary signal for story #32.
- **Rubric failures** flag responses worth manual review for story #35; they do not block CI in v0.1.

See `docs/02_testing/EVAL_STRATEGY.md` for the overall evaluation approach.
