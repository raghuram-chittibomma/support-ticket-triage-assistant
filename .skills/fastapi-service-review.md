# Skill: FastAPI Service Review

Used by: Code Reviewer Agent.

## Checklist

- [ ] Request/response models are Pydantic schemas matching `docs/01_architecture/DATA_MODEL.md`.
- [ ] Input validation errors return clear 4xx responses, not unhandled exceptions.
- [ ] No blocking/long-running calls (e.g. LLM calls) without appropriate async handling.
- [ ] Configuration (API keys, thresholds) comes from `src/config.py`, not hardcoded values.
- [ ] Endpoint has at least one integration test using `TestClient`.
- [ ] No persistence/database code introduced unless PostgreSQL has been explicitly adopted via ADR.
