# ADR-001: v0.1 Architecture Choice — Simple Pipeline Over Extensible Framework Stack

## Status

Accepted — 2026-07-02

## Context

Two architecture options were considered for the Support Ticket Triage Assistant:

**Option A — Simple:** FastAPI service + Gradio UI, an in-process Python pipeline (plain functions/classes, no LangGraph), deterministic rule modules for readiness/missing-info/priority/confidence/human-review, OpenAI-backed classification explanation and response drafting, file-based synthetic data (JSON), keyword/tag-based retrieval over a small knowledge base (no vector database), pytest plus a scripted eval runner.

**Option B — Extensible:** Same layers, plus a LangGraph graph orchestrating the pipeline, ChromaDB for semantic retrieval, PostgreSQL (with migration files) for ticket/triage/audit/eval persistence, and a provider-agnostic LLM client abstraction.

## Decision

Adopt **Option A** for v0.1.

## Rationale

- The triage workflow is a fixed, linear sequence of steps with no branching or looping requirement yet — LangGraph would add orchestration machinery without solving a real problem at this scale.
- The v0.1 knowledge base is small and curated; keyword/tag-based retrieval is expected to perform adequately, and semantic search (ChromaDB) is not yet justified.
- v0.1 has no requirement for ticket history, audit trail, or cross-session persistence, so PostgreSQL would add operational and schema-migration overhead without a corresponding requirement.
- This is a single-user portfolio/demo project; project guardrails explicitly call for avoiding unnecessary enterprise complexity and using AI/infrastructure only where it adds clear value.

## Mitigating Lock-In

To keep Option B available later without a rewrite, v0.1 code is written behind small interfaces:

- `LLMClient` abstracts the OpenAI call.
- `Retriever` abstracts keyword retrieval (a `ChromaRetriever` could implement the same interface later).
- `TriageRepository` is a documented-but-unimplemented persistence seam.
- `triage_pipeline.py` is a plain orchestration function/class that could be reimplemented as a LangGraph graph without changing the API/service layer's contract.

## Consequences

- Faster path to a working v0.1 demo with less infrastructure to stand up and maintain.
- Revisit this decision if: the knowledge base grows large enough that keyword retrieval degrades noticeably, the workflow needs branching/iterative clarification loops, or a real requirement emerges for ticket history/audit trail/evaluation-run tracking across sessions.
- Tracked as open questions in `docs/00_project/AI_ORCHESTRATOR_BRIEF.md` Section 16.
