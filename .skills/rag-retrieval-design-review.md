# Skill: RAG/Retrieval Design Review

Used by: Solution Architect Agent. Applies to the knowledge-base retrieval layer.

## Checklist

- [ ] Retrieval approach matches the current ADR (keyword/tag-based for v0.1; semantic/vector only if a future ADR justifies it).
- [ ] Every retrieved snippet carries a stable `doc_id` for citation in `references`.
- [ ] Retrieval degrades gracefully (returns no references rather than a fabricated one) when nothing matches well.
- [ ] Response drafting only cites references actually returned by the retriever — no fabricated citations.
- [ ] If/when semantic retrieval (ChromaDB) is introduced, it implements the same `Retriever` interface so the pipeline/API contract is unchanged.
