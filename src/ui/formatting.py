"""Format `TriageResult` values for display in the Gradio demo UI."""

from src.schemas import TriageResult


def format_references(result: TriageResult) -> str:
    if not result.references:
        return "_No knowledge-base references matched this ticket._"
    lines = []
    for reference in result.references:
        lines.append(f"- **{reference.doc_id}** — {reference.title}\n  > {reference.excerpt}")
    return "\n".join(lines)


def format_readiness(result: TriageResult) -> str:
    if result.readiness.is_ready:
        return "**Ready** — the ticket contains the information needed for its category."
    missing = ", ".join(f"`{field}`" for field in result.readiness.missing_fields)
    return f"**Not ready** — missing: {missing}"


def format_human_review(result: TriageResult) -> str:
    if result.human_review_required:
        reason = result.human_review_reason or "No reason provided."
        return f"**Yes — human review required.** {reason}"
    return "**No** — the agent can act on this suggestion directly."


def format_triage_result(result: TriageResult) -> str:
    """Render a complete triage result as readable Markdown for the UI output panel."""
    return f"""## Category
**{result.category.value}** (confidence {result.category_confidence:.0%})

{result.category_explanation}

## Priority
**{result.priority.value}** — {result.priority_reason}

## Readiness
{format_readiness(result)}

## Likely issue
{result.likely_issue}

## Suggested next action
{result.suggested_next_action}

## Draft customer response
{result.suggested_response}

## References
{format_references(result)}

## Overall confidence
**{result.confidence_level.upper()}**

## Human review
{format_human_review(result)}
"""
