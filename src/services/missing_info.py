"""Deterministic per-category missing-information detection.

Rules and keyword lists here are the implementation of docs/01_architecture/DATA_MODEL.md
Section 4 ("Per-Category Required-Field Rules"). That doc is the source of truth for the
rule *design*; this module is the source of truth for the exact keyword strings, and the
two must be kept in sync (see ADR-002).

A required field is considered present if the ticket's subject or body contains any one
of its associated keyword phrases (case-insensitive substring match). This intentionally
treats information already stated in free text as satisfying the requirement, per
.skills/ticket-readiness-rule-design.md ("avoid false positives when the ticket text
already implies the answer").
"""

from src.schemas import Category, TicketInput

FIELD_KEYWORDS: dict[str, list[str]] = {
    "router_band": ["2.4ghz", "2.4 ghz", "5ghz", "5 ghz", "network band", "ghz band"],
    "firmware_version": ["firmware version", "app version", "software version", "firmware v"],
    "paired_device": [
        "iphone",
        "android",
        "ipad",
        "macbook",
        "laptop",
        "windows pc",
        "samsung",
        "pixel",
        "smartphone",
    ],
    "volume_level": [
        "turned up to",
        "volume up to",
        "at max volume",
        "at low volume",
        "at high volume",
        "volume level",
    ],
    "source_device": [
        "from my phone",
        "from my laptop",
        "via bluetooth",
        "via optical",
        "via hdmi",
        "aux input",
        "connected via",
    ],
    "speaker_model_or_spec": ["ohm", "ohms", "watts", "wattage", "impedance"],
    "crossover_or_room": ["crossover", "square feet", "room size", "sq ft", "placement in the room"],
    "purchase_date": ["bought it", "purchased it", "purchase date", "bought this", "ordered it", "bought my"],
    "steps_to_reproduce": [
        "happens when",
        "occurs when",
        "every time i",
        "started after",
        "began when",
        "started happening",
    ],
    "order_number": ["order #", "order number", "order id", "ord-", "confirmation number"],
    "damage_description": [
        "dented",
        "cracked",
        "broken box",
        "damaged box",
        "smashed",
        "crushed",
        "damaged during shipping",
    ],
    "return_reason": [
        "want to return",
        "requesting a return",
        "return because",
        "reason for return",
        "no longer need",
        "would like to return",
    ],
    "proof_of_purchase": ["receipt", "proof of purchase", "invoice", "order confirmation"],
}

REQUIRED_FIELDS_BY_CATEGORY: dict[Category, list[str]] = {
    Category.WIFI_NETWORK: ["router_band", "firmware_version"],
    Category.BLUETOOTH_PAIRING: ["paired_device", "firmware_version"],
    Category.FIRMWARE_UPDATE: ["firmware_version"],
    Category.SOUND_QUALITY: ["volume_level", "source_device"],
    Category.AMP_SPEAKER_COMPATIBILITY: ["speaker_model_or_spec"],
    Category.SUBWOOFER_SETUP: ["crossover_or_room"],
    Category.PRODUCT_DEFECT: ["purchase_date", "steps_to_reproduce"],
    Category.SHIPPING_DAMAGED: ["order_number", "damage_description"],
    Category.RETURNS_REFUNDS: ["order_number", "return_reason"],
    Category.WARRANTY_REGISTRATION: ["purchase_date", "proof_of_purchase"],
    Category.ORDER_ACCOUNT_BILLING: ["order_number"],
    Category.SETUP_INSTALLATION: [],
    Category.GENERAL_QUESTION: [],
}


def _field_is_present(field: str, text: str) -> bool:
    keywords = FIELD_KEYWORDS[field]
    return any(keyword in text for keyword in keywords)


def get_missing_fields(ticket: TicketInput, category: Category) -> list[str]:
    """Return the list of required fields for `category` not evidenced in the ticket text.

    Deterministic: the same (ticket, category) pair always yields the same result.
    """
    required_fields = REQUIRED_FIELDS_BY_CATEGORY[category]
    if not required_fields:
        return []

    text = f"{ticket.subject} {ticket.body}".lower()
    return [field for field in required_fields if not _field_is_present(field, text)]
