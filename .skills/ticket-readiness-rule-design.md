# Skill: Ticket Readiness Rule Design

Used by: Solution Architect Agent, Test/Eval Designer Agent.

## Checklist

- [ ] Required fields per category are explicit and documented (e.g. Wi-Fi issues require product model, network band, firmware/app version).
- [ ] Rules are deterministic — same input always yields the same readiness verdict and missing-field list.
- [ ] Rules avoid false positives for "missing info" when the ticket text already implies the answer (e.g. product SKU mentioned by name in the body).
- [ ] Every rule is covered by at least one unit test with a complete ticket (passes) and one incomplete ticket (correctly flags missing fields).
- [ ] Rule thresholds/required-field lists live in a single, clearly named location (e.g. `src/services/missing_info.py`) rather than scattered across the codebase.
