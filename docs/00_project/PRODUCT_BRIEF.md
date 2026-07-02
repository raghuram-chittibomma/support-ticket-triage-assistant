# Product Brief — Support Ticket Triage Assistant

## Problem Statement

NorthPeak Audioworks support agents manually re-read each incoming ticket, judge its category and urgency, decide whether they have enough information to act, and search scattered FAQ/policy content before drafting a reply. This is slow, inconsistent across agents, and error-prone for a hi-fi product line with many setup- and connectivity-related issues.

## Personas

- **Support Agent (primary):** Handles incoming tickets daily; needs fast, trustworthy triage to reduce time-to-first-response.
- **Support Lead:** Monitors ticket quality/escalations; cares about consistent categorization and priority accuracy.
- **Product Owner:** Prioritizes roadmap features; cares about demo value and extensibility.
- **QA Analyst:** Verifies correctness of triage output against known scenarios.
- **Engineering Support:** Maintains and extends the system; cares about explainability and clean architecture.

## Core Workflow

1. Support agent pastes/types a raw ticket description into the assistant.
2. Assistant checks whether the ticket has enough information to triage confidently.
3. If incomplete, the assistant flags missing details (e.g., product model, firmware version, network type).
4. Assistant classifies the ticket into a category and estimates priority.
5. Assistant retrieves relevant synthetic FAQ/policy/troubleshooting snippets, if applicable.
6. Assistant drafts a suggested customer response grounded in the retrieved references.
7. Assistant reports a confidence level and flags tickets that need human review.
8. Agent reviews the output, edits if needed, and responds to the customer (outside this system in v0.1).

## Functional Requirements

- FR1: Accept a free-text ticket (subject + body, optionally product SKU/persona/channel).
- FR2: Deterministically assess ticket readiness (enough information to act) and list missing fields if not ready.
- FR3: Classify the ticket into one of the defined categories (see taxonomy below) with an explanation.
- FR4: Estimate priority (Urgent / High / Medium / Low) using deterministic rules.
- FR5: Retrieve relevant knowledge-base snippets (FAQ, policy, troubleshooting, firmware notes) when applicable, with citations.
- FR6: Draft a suggested customer response grounded in retrieved references.
- FR7: Produce an overall confidence level and a human-review-required flag with a reason.
- FR8: Return all of the above as a single structured result (category, priority, readiness, likely issue, next action, draft response, references, confidence, human-review flag).

## Non-Functional Requirements

- NFR1: Readiness, missing-info detection, priority, and human-review logic must be deterministic and explainable (no LLM randomness in pass/fail gates).
- NFR2: LLM usage is confined to classification explanation, response drafting, summarization, and ambiguity handling.
- NFR3: Local-first development; no required cloud infrastructure beyond an LLM API call.
- NFR4: All data synthetic — see the synthetic-data-only rule in the orchestrator brief.
- NFR5: Interactive-demo-appropriate latency (target under ~5 seconds per ticket in typical cases).
- NFR6: Codebase small and explainable, appropriate for a single-user portfolio project.

## Category Taxonomy (v0.1)

1. Setup / Installation
2. Wi-Fi / Network Connectivity
3. Bluetooth / Pairing
4. Firmware Update
5. Sound Quality / Distortion
6. Amplifier / Speaker Compatibility
7. Subwoofer Setup
8. Product Defect / Hardware Issue
9. Shipping / Damaged Delivery
10. Returns / Refunds
11. Warranty / Registration
12. Order / Account / Billing
13. General Product Question

*(Refined from the original brainstormed list by merging Billing/Payment and Account Management into a single "Order / Account / Billing" category to reduce overlap for a small v0.1 taxonomy; may be re-split later if warranted by real usage data from evaluation scenarios.)*

## In Scope (v0.1)

Single-ticket triage workflow (FR1–FR8 above), synthetic data (catalog, tickets, KB), deterministic readiness/priority/human-review logic, OpenAI-backed classification explanation and response drafting, keyword-based retrieval, FastAPI endpoint, Gradio UI, pytest suite, evaluation scenarios, release notes.

## Out of Scope (v0.1)

Authentication/multi-user, ticket persistence/history/audit trail, PostgreSQL, real integrations (helpdesk/CRM/messaging), semantic/vector retrieval, LangGraph orchestration, multilingual support, batch ticket processing.

## Assumptions

- One ticket processed per request; English only; OpenAI API key available via environment variable; no PII anywhere because data is synthetic; single developer + AI agents drive delivery.

## Open Questions

See `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` Section 16 (confidence-score weighting, future PostgreSQL need, future semantic retrieval need, future LangGraph need). Tracked and revisited per milestone, not duplicated here.
