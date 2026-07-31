# Skill: Prompt Caching Review

Used by: Solution Architect Agent, Code Reviewer Agent.

## Checklist

- [ ] Cacheable prefixes match ADR-005: static system/tool schema, eligible history, judge rubric.
- [ ] Cacheable blocks are stable across requests (no per-request randomness inside the cached prefix).
- [ ] Model/region support is verified; if unsupported, traces show `cache_enabled=false`.
- [ ] Observability records cache hit/miss and token savings when the API provides them.
- [ ] README/release notes do not claim caching savings without scorecard/observability evidence.
- [ ] Eval judge prompts keep the rubric prefix eligible for caching.
