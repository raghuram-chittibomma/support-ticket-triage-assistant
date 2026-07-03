# Skill: FastAPI Service Review

Used by: Code Reviewer Agent.

## Checklist

- [ ] Request/response models are Pydantic schemas matching `{{project.docs.data_model}}`.
- [ ] Input validation errors return clear 4xx responses, not unhandled exceptions.
- [ ] No blocking/long-running calls (e.g. LLM calls) without appropriate async handling.
- [ ] Configuration (API keys, thresholds) comes from the project's config module, not hardcoded values.
- [ ] Endpoint has at least one integration test using `TestClient`.
- [ ] No persistence/database code introduced unless PostgreSQL has been explicitly adopted via ADR.
