"""Scripted LLM client for reproducible eval runs (no API key, no network)."""

from __future__ import annotations

import json

from evals.loader import load_eval_scenarios
from src.schemas import Category


class PerScenarioScriptedLLM:
    """Returns each scenario's expected category for classification; generic draft otherwise."""

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        if "Choose exactly one category" not in system_prompt:
            return json.dumps(
                {
                    "likely_issue": "Issue described in ticket.",
                    "suggested_next_action": "Follow up with customer.",
                    "suggested_response": (
                        "Thanks for reaching out — we can help with your speaker issue."
                    ),
                }
            )
        category = Category.GENERAL_QUESTION.value
        for scenario in load_eval_scenarios():
            if scenario.ticket.subject in user_prompt or scenario.ticket.body[:40] in user_prompt:
                category = scenario.expected_category.value
                break
        return json.dumps({"category": category, "explanation": f"Matches {category}."})
