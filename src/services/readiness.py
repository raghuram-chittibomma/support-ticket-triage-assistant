"""Deterministic ticket readiness checking.

Does a submitted ticket contain enough information to triage confidently for its
category? This is a thin wrapper over src.services.missing_info: readiness is defined
purely as "no required fields are missing" (docs/01_architecture/DATA_MODEL.md Section 1).
No LLM call is involved - see docs/01_architecture/ARCHITECTURE.md for the note on why
this runs after classification rather than before.
"""

from src.schemas import Category, ReadinessResult, TicketInput
from src.services.missing_info import get_missing_fields


def check_readiness(ticket: TicketInput, category: Category) -> ReadinessResult:
    """Return the deterministic readiness verdict for `ticket` given its `category`."""
    missing_fields = get_missing_fields(ticket, category)
    return ReadinessResult(is_ready=len(missing_fields) == 0, missing_fields=missing_fields)
