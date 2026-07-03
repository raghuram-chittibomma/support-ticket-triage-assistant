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

## 4. Priority Rule Keyword Detail

Keyword-based, case-insensitive substring matching against `subject + body`, evaluated in this order (first match wins):

1. **Urgent — safety:** any of `burning smell`, `smoke`, `electrical smell`, `shock`, `sparks`, `caught fire`, `fire hazard`.
2. **Urgent — total failure + deadline:** a total-failure keyword (see #3 below) AND a deadline keyword: `return window`, `return deadline`, `need this resolved by`, `before my return period ends`.
3. **High — total failure:** `won't turn on`, `won't power on`, `doesn't turn on`, `no sound at all`, `won't connect`, `can't connect`, `stopped connecting`, `not connecting at all`, `won't pair`, `completely dead`, `not working at all`, `no power at all`.
4. **High — escalation:** `called multiple times`, `contacted you before`, `spoken to someone already`, `very frustrated`, `this is unacceptable`, `third time`, `charged twice`, `charged me twice`, `double charged`.
5. **Low — informational/administrative/cosmetic:** `is it worth`, `is that a safe`, `is that a reasonable`, `wondering if`, `not sure if`, `not sure how`, `curious what`, `curious how`, `how do i`, `how long does`, `want to register`, `would like to return`, `requesting a return`, `check on`, `question about`, `should i`, `is it safe to`, `trying to figure out`, `instructions aren't very clear`, `beat up`, `haven't opened it yet`, `don't think i want to keep`, `still have the receipt`, `dent`, `dented`, `a scratch on`, `scratched`, `scuffed`, `cosmetic`. All keyword matching uses word-boundary matching (a keyword must appear as standalone word(s), not embedded inside another word — e.g. `dent` matches "a visible dent" but not "identify") to avoid substring false positives.
6. **Medium — default:** none of the above matched. A described, ongoing problem with no urgent/high/low signal is treated as an intermittent or partial issue by default, per the Section 3 rule text.

This table is the single source of truth for both `src/services/priority.py` and the `expected_priority` ground truth in `data/sample/tickets.json` — they must stay consistent (see ADR-002).

## 5. Per-Category Required-Field Rules (Readiness / Missing-Information)

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

## 6. Synthetic Data File Structures

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

## 7. Metadata Fields (consistent across datasets)

`id`/`doc_id`, `type` or category tag(s), product tag(s) where applicable, and — for KB content — `last_updated`, so every retrievable/citable item has a stable identity.

## 8. Source Citation Strategy

Every KB article has a stable `doc_id`. When the retriever selects an article for a ticket, the triage output's `references` field includes `doc_id`, `title`, and a short `excerpt`, so a support agent (or an evaluator) can trace a suggested response back to the specific synthetic knowledge source used.

## 9. Synthetic Data Supporting Tests and Evaluation

The same `tickets.json` dataset is used three ways: (1) unit-test fixtures for individual services (readiness, priority, classifier), (2) integration-test inputs for the full pipeline/API, and (3) evaluation ground truth (`expected_category`, `expected_priority`, `expected_missing_fields`) for the eval scenario runner in `evals/`. This avoids maintaining three separate datasets.

## 10. Forward-Looking Relational Schema (v0.2+, not implemented in v0.1)

If PostgreSQL is adopted, the following tables are anticipated (introduced via migration files under `db/migrations/`, never ad hoc):

- `tickets` — persisted ticket submissions (id, subject, body, product_sku, customer_persona, channel, submitted_at).
- `triage_results` — persisted triage output per ticket (foreign key to `tickets`, category, priority, confidence, human_review_required, created_at).
- `eval_runs` — evaluation run metadata (id, run_at, scenario_set_version, summary_metrics).
- `eval_run_results` — per-scenario results within an `eval_run` (expected vs. actual values).
- `feedback` — optional agent feedback on a triage result (ticket_id, rating, comment, created_at).

## 11. Data Rule

No real customer, employer, production, proprietary, or sensitive data may be used anywhere in this repository. All values in the examples above are fictional.

## 12. Confidence Scoring Formula (deterministic)

Implemented in `src/services/confidence.py`. Resolves the open question in `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` Section 16 ("exact weighting formula for the confidence score"). No LLM call — a deterministic combination of three already-computed upstream signals:

1. Start from the classifier's `category_confidence` (0.0–1.0, from `src/services/classifier.py` — see `DATA_MODEL.md`'s classifier design and `ARCHITECTURE.md`).
2. **Readiness penalty:** if `readiness.is_ready` is `False`, subtract `0.25`. Missing required information directly reduces how much the result can be trusted/acted on.
3. **Retrieval bonus:** if the retriever (`src/retrieval/kb_retriever.py`) returned one or more references, add `0.05`. Grounding in a real knowledge-base article is a (small) positive signal. An **empty** reference list is treated as *neutral*, not negative — KB coverage is intentionally partial (only 9 of 13 categories have any articles as of Slice 3, per ADR-002's synthetic-data scope), so "no references" is expected and unrelated to classification/readiness quality for those categories.
4. Clamp the combined score to `[0.0, 1.0]`.
5. Map to `confidence_level`: `high` if score ≥ `0.75`; `medium` if score ≥ `0.5`; otherwise `low`.

These thresholds are a starting point for the v0.1 demo, not empirically tuned — revisit once the evaluation scenario suite (#26) provides real accuracy/calibration data (see `docs/02_testing/EVAL_STRATEGY.md`'s "Confidence calibration" dimension).

## 13. Human-Review Decision Rules (deterministic)

Implemented in `src/services/human_review.py`. No LLM call — an ordered, explainable rule list (first matching rule wins), consuming already-computed `priority`, `confidence_level`, and `readiness`, plus a direct escalation-language check against the ticket text:

1. **Priority is Urgent →** always flagged. `Priority.URGENT` is only reached via safety-related language or total-failure-plus-deadline (`DATA_MODEL.md` Section 4), both of which unconditionally warrant a human's judgment.
2. **Escalation language detected in the ticket text →** always flagged, independent of which priority tier resulted. Reuses the same `ESCALATION_KEYWORDS` list from `src/services/priority.py` (via `detect_escalation_language`) rather than duplicating it, so it stays in sync with the priority rules by construction.
3. **`confidence_level` is `low` →** flagged.
4. **`confidence_level` is `medium` AND the ticket is not ready →** flagged (the combination of moderate uncertainty and missing information is treated as more risky than either alone).
5. **Otherwise →** not flagged.
