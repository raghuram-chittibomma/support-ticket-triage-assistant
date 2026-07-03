"""Load evaluation scenarios from the synthetic ticket dataset."""

from __future__ import annotations

from dataclasses import dataclass

from src.data_access import load_sample_tickets
from src.schemas import Category, Priority, TicketInput


@dataclass(frozen=True)
class EvalScenario:
    """One ticket plus ground-truth fields from data/sample/tickets.json."""

    ticket_id: str
    ticket: TicketInput
    expected_category: Category
    expected_priority: Priority
    expected_missing_fields: list[str]


def _to_ticket_input(raw: dict) -> TicketInput:
    return TicketInput(
        ticket_id=raw["ticket_id"],
        subject=raw["subject"],
        body=raw["body"],
        product_sku=raw.get("product_sku"),
        customer_persona=raw.get("customer_persona"),
        channel=raw.get("channel"),
    )


def load_eval_scenarios() -> list[EvalScenario]:
    """Load all evaluation scenarios from data/sample/tickets.json."""
    scenarios: list[EvalScenario] = []
    for raw in load_sample_tickets():
        scenarios.append(
            EvalScenario(
                ticket_id=raw["ticket_id"],
                ticket=_to_ticket_input(raw),
                expected_category=Category(raw["expected_category"]),
                expected_priority=Priority(raw["expected_priority"]),
                expected_missing_fields=list(raw["expected_missing_fields"]),
            )
        )
    return scenarios
