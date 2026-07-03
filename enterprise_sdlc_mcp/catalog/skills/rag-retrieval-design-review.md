# Skill: RAG/Retrieval Design Review

Used by: Solution Architect Agent. Applies to knowledge-base or document retrieval layers.

## Checklist

- [ ] Retrieval approach matches the current ADR (keyword/tag-based unless a future ADR justifies semantic/vector search).
- [ ] Every retrieved snippet carries a stable identifier for citation in responses.
- [ ] Retrieval degrades gracefully (returns no references rather than a fabricated one) when nothing matches well.
- [ ] Response drafting only cites references actually returned by the retriever — no fabricated citations.
- [ ] If/when semantic retrieval is introduced, it implements the same retriever interface so the pipeline/API contract is unchanged.
