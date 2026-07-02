# Data Model — Support Ticket Triage Assistant

## v0.1 Persistence Decision

File-based synthetic JSON is sufficient for v0.1 (no PostgreSQL). See `docs/01_architecture/DECISIONS/ADR-001-architecture-choice.md`. The relational schema in Section 5 below is a **forward-looking design only** — it documents what a v0.2 PostgreSQL adoption would look like, but no migrations exist yet and no code depends on it.

## 1. Ticket Schema (Pydantic, `src/schemas/`)

**TicketInput** (request):

- `ticket_id: str | None` — generated if absent.
- `subject: str`
- `body: str`
- `product_sku: str | None`
- `customer_persona: str | None`
- `channel: Literal["email", "chat", "phone"] | None`
- `submitted_at: datetime | None`

**TriageResult** (response):

- `category: Category`
- `category_confidence: float` (0–1)
- `category_explanation: str`
- `priority: Priority`
- `priority_reason: str`
- `readiness: ReadinessResult` — `{ is_ready: bool, missing_fields: list[str] }`
- `likely_issue: str`
- `suggested_next_action: str`
- `suggested_response: str`
- `references: list[Reference]` — `{ doc_id: str, title: str, excerpt: str }`
- `confidence_level: Literal["high", "medium", "low"]`
- `human_review_required: bool`
- `human_review_reason: str | None`

## 2. Category Taxonomy

`Setup / Installation`, `Wi-Fi / Network Connectivity`, `Bluetooth / Pairing`, `Firmware Update`, `Sound Quality / Distortion`, `Amplifier / Speaker Compatibility`, `Subwoofer Setup`, `Product Defect / Hardware Issue`, `Shipping / Damaged Delivery`, `Returns / Refunds`, `Warranty / Registration`, `Order / Account / Billing`, `General Product Question`.

## 3. Priority Rules (deterministic)

- **Urgent:** safety-related keywords (e.g. burning smell, smoke, shock) OR total product failure combined with a shipping/return deadline.
- **High:** complete loss of function (no sound, won't power on, won't connect at all) OR escalation language from the customer (e.g. repeated contact, explicit frustration/threat to return).
- **Medium:** intermittent or partial issue with a known workaround (e.g. occasional dropouts, one-band Wi-Fi issue).
- **Low:** informational or cosmetic (e.g. general product question, minor cosmetic defect, "how do I..." questions).

Rules are implemented as an ordered, explainable rule list in `src/services/priority.py` — first matching rule wins, and the matched rule is returned as `priority_reason`.

## 4. Per-Category Required-Field Rules (Readiness / Missing-Information)

Deterministic, keyword-based rules used by `src/services/missing_info.py`. A field is considered **present** if the ticket body contains any one of its associated keyword phrases (case-insensitive substring match) — this deliberately treats information stated in free text as satisfying the requirement, per `.skills/ticket-readiness-rule-design.md` ("avoid false positives when the ticket text already implies the answer"). Categories not listed require no additional fields (always ready from a readiness standpoint).

| Category | Required fields | Detection keywords (any match = present) |
|---|---|---|
| Wi-Fi / Network Connectivity | `router_band`, `firmware_version` | `router_band`: "2.4ghz", "2.4 ghz", "5ghz", "5 ghz", "network band", "ghz band" · `firmware_version`: "firmware version", "app version", "software version", "firmware v" |
| Bluetooth / Pairing | `paired_device`, `firmware_version` | `paired_device`: "iphone", "android", "ipad", "macbook", "laptop", "windows pc", "samsung", "pixel", "smartphone" · `firmware_version`: (same as above) |
| Firmware Update | `firmware_version` | (same as above) |
| Sound Quality / Distortion | `volume_level`, `source_device` | `volume_level`: "turned up to", "volume up to", "at max volume", "at low volume", "at high volume", "volume level" · `source_device`: "from my phone", "from my laptop", "via bluetooth", "via optical", "via hdmi", "aux input", "connected via" |
| Amplifier / Speaker Compatibility | `speaker_model_or_spec` | "ohm", "ohms", "watts", "wattage", "impedance" |
| Subwoofer Setup | `crossover_or_room` | "crossover", "square feet", "room size", "sq ft", "placement in the room" |
| Product Defect / Hardware Issue | `purchase_date`, `steps_to_reproduce` | `purchase_date`: "bought it", "purchased it", "purchase date", "bought this", "ordered it", "bought my" · `steps_to_reproduce`: "happens when", "occurs when", "every time i", "started after", "began when", "started happening" |
| Shipping / Damaged Delivery | `order_number`, `damage_description` | `order_number`: "order #", "order number", "order id", "ord-", "confirmation number" · `damage_description`: "dented", "cracked", "broken box", "damaged box", "smashed", "crushed", "damaged during shipping" |
| Returns / Refunds | `order_number`, `return_reason` | `order_number`: (same as above) · `return_reason`: "want to return", "requesting a return", "return because", "reason for return", "no longer need", "would like to return" |
| Warranty / Registration | `purchase_date`, `proof_of_purchase` | `purchase_date`: (same as above) · `proof_of_purchase`: "receipt", "proof of purchase", "invoice", "order confirmation" |
| Order / Account / Billing | `order_number` | (same as above) |
| Setup / Installation | *(none)* | always ready |
| General Product Question | *(none)* | always ready |

This table is the single source of truth for both the missing-info detector implementation and the `expected_missing_fields` ground truth in `data/sample/tickets.json` — they must stay consistent (see ADR-002).

## 5. Synthetic Data File Structures

**`data/sample/products.json`** — one entry per SKU:

```json
{
  "sku": "SUM1-ACT",
  "name": "Summit One Active",
  "product_type": "Powered bookshelf speaker",
  "category_hints": ["Wi-Fi / Network Connectivity", "Bluetooth / Pairing", "Setup / Installation"],
  "short_description": "Powered bookshelf speaker with Wi-Fi streaming and Bluetooth.",
  "common_issues": ["Wi-Fi reconnect after firmware update", "Bluetooth pairing drops", "App setup fails to discover speaker"]
}
```

**`data/sample/tickets.json`** — one entry per sample/eval ticket:

```json
{
  "ticket_id": "TCK-0001",
  "subject": "Speakers won't reconnect to Wi-Fi after update",
  "body": "My Summit One Active speakers stopped connecting to Wi-Fi right after the last firmware update...",
  "product_sku": "SUM1-ACT",
  "customer_persona": "returning-customer",
  "channel": "email",
  "expected_category": "Wi-Fi / Network Connectivity",
  "expected_priority": "High",
  "expected_missing_fields": ["router_band", "app_version"]
}
```

**`data/knowledge_base/*.json`** — one entry per KB article:

```json
{
  "doc_id": "KB-WIFI-004",
  "title": "Resolving Wi-Fi reconnect issues after firmware updates",
  "type": "troubleshooting",
  "category_tags": ["Wi-Fi / Network Connectivity", "Firmware Update"],
  "product_tags": ["SUM1-ACT", "CDR-STRM-MINI"],
  "content": "If your speaker does not reconnect after a firmware update, first power-cycle the speaker...",
  "last_updated": "2026-05-01"
}
```

## 6. Metadata Fields (consistent across datasets)

`id`/`doc_id`, `type` or category tag(s), product tag(s) where applicable, and — for KB content — `last_updated`, so every retrievable/citable item has a stable identity.

## 7. Source Citation Strategy

Every KB article has a stable `doc_id`. When the retriever selects an article for a ticket, the triage output's `references` field includes `doc_id`, `title`, and a short `excerpt`, so a support agent (or an evaluator) can trace a suggested response back to the specific synthetic knowledge source used.

## 8. Synthetic Data Supporting Tests and Evaluation

The same `tickets.json` dataset is used three ways: (1) unit-test fixtures for individual services (readiness, priority, classifier), (2) integration-test inputs for the full pipeline/API, and (3) evaluation ground truth (`expected_category`, `expected_priority`, `expected_missing_fields`) for the eval scenario runner in `evals/`. This avoids maintaining three separate datasets.

## 9. Forward-Looking Relational Schema (v0.2+, not implemented in v0.1)

If PostgreSQL is adopted, the following tables are anticipated (introduced via migration files under `db/migrations/`, never ad hoc):

- `tickets` — persisted ticket submissions (id, subject, body, product_sku, customer_persona, channel, submitted_at).
- `triage_results` — persisted triage output per ticket (foreign key to `tickets`, category, priority, confidence, human_review_required, created_at).
- `eval_runs` — evaluation run metadata (id, run_at, scenario_set_version, summary_metrics).
- `eval_run_results` — per-scenario results within an `eval_run` (expected vs. actual values).
- `feedback` — optional agent feedback on a triage result (ticket_id, rating, comment, created_at).

## 10. Data Rule

No real customer, employer, production, proprietary, or sensitive data may be used anywhere in this repository. All values in the examples above are fictional.
