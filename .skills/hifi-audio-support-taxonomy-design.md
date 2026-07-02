# Skill: Hi-Fi Audio Support Taxonomy Design

Used by: Product Analyst Agent, Solution Architect Agent.

## Checklist

- [ ] Categories are mutually distinguishable for a support agent skimming a ticket (minimal overlap between adjacent categories).
- [ ] Categories map cleanly onto realistic hi-fi/audio scenarios (Wi-Fi, Bluetooth, firmware, distortion, amp/speaker compatibility, subwoofer setup, shipping/returns/warranty, general questions) — see `docs/00_project/PRODUCT_BRIEF.md`.
- [ ] Every synthetic product in the catalog maps to at least one plausible category via its `common_issues`/`category_hints`.
- [ ] Taxonomy size stays small enough for a v0.1 demo (roughly 10-15 categories) — resist adding categories without a concrete supporting scenario.
- [ ] Changes to the taxonomy are reflected consistently across `DATA_MODEL.md`, `PRODUCT_BRIEF.md`, and the classifier/priority rule implementations.
