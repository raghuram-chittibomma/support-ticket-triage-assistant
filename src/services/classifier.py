"""Ticket classifier: keyword pre-filter + LLM confirmation. See ARCHITECTURE.md and #16.

Two stages:
1. A deterministic keyword pre-filter (`rank_categories`) scores every taxonomy category
   against the ticket text and the product's `category_hints`, producing a shortlist.
2. The shortlist is passed to an `LLMClient` (never a direct provider call — see
   `.skills/architecture-review.md`) which makes the final call and supplies a
   human-readable explanation.

`category_confidence` is a deterministic function of how well the LLM's choice agrees with
the keyword pre-filter, not a further model call — this keeps confidence explainable.
"""

import json
from functools import lru_cache

from pydantic import BaseModel, Field

from src.data_access import load_products
from src.llm import LLMClient
from src.schemas import Category, TicketInput

CATEGORY_KEYWORDS: dict[Category, list[str]] = {
    Category.SETUP_INSTALLATION: [
        "set up",
        "setup",
        "install",
        "assemble",
        "assembly",
        "unbox",
        "installation",
        "base plate",
    ],
    Category.WIFI_NETWORK: [
        "wi-fi",
        "wifi",
        "network",
        "router",
        "5ghz",
        "2.4ghz",
        "connect to wi-fi",
        "wireless network",
    ],
    Category.BLUETOOTH_PAIRING: [
        "bluetooth",
        "pair",
        "pairing",
        "paired",
    ],
    Category.FIRMWARE_UPDATE: [
        "firmware",
        "update",
        "upgrade",
        "new version",
    ],
    Category.SOUND_QUALITY: [
        "distorted",
        "crackly",
        "buzzing",
        "hum",
        "muddy",
        "sound quality",
        "static",
        "unclear",
    ],
    Category.AMP_SPEAKER_COMPATIBILITY: [
        "amp",
        "amplifier",
        "ohms",
        "watts",
        "impedance",
        "drive them",
        "powerful enough",
        "compatib",
    ],
    Category.SUBWOOFER_SETUP: [
        "subwoofer",
        "crossover",
        "bass",
        "sub ",
    ],
    Category.PRODUCT_DEFECT: [
        "defect",
        "broken",
        "doesn't work",
        "malfunction",
        "one channel",
        "unresponsive",
        "hardware issue",
        "stopped working",
    ],
    Category.SHIPPING_DAMAGED: [
        "arrived damaged",
        "box was crushed",
        "dented",
        "shipping",
        "damaged in shipping",
        "beat up",
        "crushed",
    ],
    Category.RETURNS_REFUNDS: [
        "return",
        "refund",
        "send it back",
        "requesting a return",
    ],
    Category.WARRANTY_REGISTRATION: [
        "warranty",
        "register",
        "registration",
        "receipt",
        "proof of purchase",
    ],
    Category.ORDER_ACCOUNT_BILLING: [
        "order",
        "billing",
        "charged",
        "account",
        "invoice",
        "payment",
    ],
    Category.GENERAL_QUESTION: [
        "curious",
        "question about",
        "wondering",
        "how long does",
        "what does",
        "just wondering",
    ],
}

CATEGORY_DESCRIPTIONS: dict[Category, str] = {
    Category.SETUP_INSTALLATION: "Help setting up, unboxing, or physically assembling a product.",
    Category.WIFI_NETWORK: "Wi-Fi connectivity, network dropouts, router configuration.",
    Category.BLUETOOTH_PAIRING: "Bluetooth pairing failures or connection drops.",
    Category.FIRMWARE_UPDATE: "Firmware update install/upgrade questions or failures.",
    Category.SOUND_QUALITY: "Distortion, buzzing, hum, or degraded audio quality.",
    Category.AMP_SPEAKER_COMPATIBILITY: "Whether an amplifier and speakers are compatible or well-matched.",
    Category.SUBWOOFER_SETUP: "Subwoofer placement, crossover, or bass output questions.",
    Category.PRODUCT_DEFECT: "A specific unit seems broken or defective (not a setup/config issue).",
    Category.SHIPPING_DAMAGED: "The package or product arrived damaged in shipping.",
    Category.RETURNS_REFUNDS: "The customer wants to return a product or get a refund.",
    Category.WARRANTY_REGISTRATION: "Registering a product or checking warranty coverage.",
    Category.ORDER_ACCOUNT_BILLING: "Order status, billing, or account questions.",
    Category.GENERAL_QUESTION: "A general question that doesn't fit the other categories.",
}


class ClassificationResult(BaseModel):
    category: Category
    category_confidence: float = Field(ge=0.0, le=1.0)
    category_explanation: str


def _ticket_text(ticket: TicketInput) -> str:
    return f"{ticket.subject} {ticket.body}".lower()


@lru_cache(maxsize=1)
def _product_category_hints() -> dict[str, list[str]]:
    return {product["sku"]: product.get("category_hints", []) for product in load_products()}


def rank_categories(ticket: TicketInput) -> list[tuple[Category, int]]:
    """Deterministic keyword/product-hint pre-filter. Returns categories sorted by score desc."""
    text = _ticket_text(ticket)
    hints = _product_category_hints().get(ticket.product_sku, []) if ticket.product_sku else []

    scores: dict[Category, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if category.value in hints:
            score += 1
        scores[category] = score

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def _build_system_prompt() -> str:
    taxonomy_lines = "\n".join(
        f"- {category.value}: {CATEGORY_DESCRIPTIONS[category]}" for category in Category
    )
    return (
        "You are classifying a customer support ticket for NorthPeak Audioworks, a home "
        "audio equipment company. Choose exactly one category from this taxonomy:\n\n"
        f"{taxonomy_lines}\n\n"
        "Respond with ONLY a JSON object of the form "
        '{"category": "<exact category name from the list above>", "explanation": '
        '"<one sentence, plain language>"}. Do not include any other text.'
    )


def _build_user_prompt(ticket: TicketInput, top_candidates: list[Category]) -> str:
    candidate_lines = "\n".join(f"- {category.value}" for category in top_candidates)
    return (
        f"Subject: {ticket.subject}\n"
        f"Body: {ticket.body}\n\n"
        "A keyword pre-filter suggests these likely categories (for reference only — pick "
        "whichever category from the full taxonomy actually fits best):\n"
        f"{candidate_lines}"
    )


def _parse_llm_response(raw: str, fallback: Category) -> tuple[Category, str]:
    try:
        data = json.loads(raw)
        category = Category(data["category"])
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return (
            fallback,
            f"Falling back to the keyword-based match ('{fallback.value}') because the "
            "model response could not be parsed as a valid taxonomy category.",
        )

    explanation = str(data.get("explanation") or "").strip()
    if not explanation:
        explanation = f"Classified as {category.value}."
    return category, explanation


def _compute_confidence(chosen: Category, ranked: list[tuple[Category, int]]) -> float:
    top_category = ranked[0][0] if ranked else None
    top_three = {category for category, _ in ranked[:3]}
    if chosen == top_category:
        return 0.9
    if chosen in top_three:
        return 0.65
    return 0.4


def classify_ticket(ticket: TicketInput, llm_client: LLMClient) -> ClassificationResult:
    ranked = rank_categories(ticket)
    top_candidates = [category for category, _ in ranked[:3]]
    fallback = top_candidates[0] if top_candidates else Category.GENERAL_QUESTION

    raw_response = llm_client.complete(
        system_prompt=_build_system_prompt(),
        user_prompt=_build_user_prompt(ticket, top_candidates),
    )
    category, explanation = _parse_llm_response(raw_response, fallback=fallback)
    confidence = _compute_confidence(category, ranked)

    return ClassificationResult(
        category=category,
        category_confidence=confidence,
        category_explanation=explanation,
    )
