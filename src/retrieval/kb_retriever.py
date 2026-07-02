"""Keyword/tag-based knowledge-base retrieval. See docs/01_architecture/ARCHITECTURE.md
'Extension seams' and .skills/rag-retrieval-design-review.md.

No vector database in v0.1 (see ADR-001). A candidate article must share the ticket's
classified `Category` via `category_tags` — this is the primary relevance signal and the
reason retrieval degrades gracefully to "no references" for categories with no matching KB
content (e.g. General Product Question), rather than returning an unrelated article. Among
same-category candidates, a deterministic keyword-overlap + product-tag score picks the
best match(es), so a future semantic `Retriever` implementation can be swapped in (e.g. a
`ChromaRetriever`) without changing callers.
"""

import re
from typing import Protocol

from src.data_access import load_knowledge_base
from src.schemas import Category, Reference, TicketInput

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been", "to",
    "of", "in", "on", "at", "for", "with", "this", "that", "it", "its", "your", "you", "if",
    "then", "not", "do", "does", "did", "from", "by", "as", "have", "has", "had", "will",
    "would", "can", "could", "i", "my", "me", "we", "our", "am", "so", "just", "get", "got",
}

_EXCERPT_MAX_LEN = 220


def _significant_words(text: str) -> set[str]:
    # Hyphenated compounds (e.g. "Wi-Fi", "power-cycle") are kept as single tokens rather
    # than split, since splitting on "-" would reduce "wi-fi" to two 2-letter fragments and
    # drop it below the length-4 significance threshold entirely.
    words = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    return {word for word in words if len(word) > 3 and word not in _STOPWORDS}


def _make_excerpt(content: str, max_len: int = _EXCERPT_MAX_LEN) -> str:
    if len(content) <= max_len:
        return content
    truncated = content[:max_len].rsplit(" ", 1)[0]
    return truncated + "..."


def _to_reference(article: dict) -> Reference:
    return Reference(
        doc_id=article["doc_id"],
        title=article["title"],
        excerpt=_make_excerpt(article["content"]),
    )


class Retriever(Protocol):
    def retrieve(self, ticket: TicketInput, category: Category) -> list[Reference]:
        """Return zero or more references relevant to this ticket/category."""
        ...


class KeywordKBRetriever:
    """Default v0.1 Retriever implementation. See module docstring for the matching strategy."""

    def __init__(self, articles: list[dict] | None = None, max_results: int = 2) -> None:
        self._articles = articles if articles is not None else load_knowledge_base()
        self._max_results = max_results

    def _score(self, ticket_words: set[str], ticket: TicketInput, article: dict) -> int:
        article_words = _significant_words(f"{article['title']} {article['content']}")
        score = len(ticket_words & article_words)
        if ticket.product_sku and ticket.product_sku in article.get("product_tags", []):
            score += 3
        return score

    def retrieve(self, ticket: TicketInput, category: Category) -> list[Reference]:
        candidates = [
            article
            for article in self._articles
            if category.value in article.get("category_tags", [])
        ]
        if not candidates:
            return []

        ticket_words = _significant_words(f"{ticket.subject} {ticket.body}")
        # Stable sort: ties keep the candidates' original (deterministic) file-load order.
        ranked = sorted(
            candidates,
            key=lambda article: self._score(ticket_words, ticket, article),
            reverse=True,
        )
        return [_to_reference(article) for article in ranked[: self._max_results]]
