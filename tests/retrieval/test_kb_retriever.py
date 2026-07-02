import pytest

from src.data_access import load_knowledge_base, load_sample_tickets
from src.retrieval.kb_retriever import KeywordKBRetriever
from src.schemas import Category, TicketInput

SAMPLE_TICKETS = load_sample_tickets()
KB_ARTICLES = load_knowledge_base()
KB_ARTICLES_BY_ID = {article["doc_id"]: article for article in KB_ARTICLES}
COVERED_CATEGORIES = {tag for article in KB_ARTICLES for tag in article["category_tags"]}


def _to_ticket_input(raw: dict) -> TicketInput:
    return TicketInput(
        ticket_id=raw["ticket_id"],
        subject=raw["subject"],
        body=raw["body"],
        product_sku=raw.get("product_sku"),
    )


class TestKeywordKBRetrieverAgainstFixtures:
    retriever = KeywordKBRetriever()

    @pytest.mark.parametrize("raw", SAMPLE_TICKETS, ids=[t["ticket_id"] for t in SAMPLE_TICKETS])
    def test_retrieval_matches_kb_coverage_by_category(self, raw: dict):
        ticket = _to_ticket_input(raw)
        category = Category(raw["expected_category"])

        references = self.retriever.retrieve(ticket, category)

        if category.value in COVERED_CATEGORIES:
            assert len(references) >= 1, f"expected at least one reference for {category.value}"
        else:
            assert references == [], f"expected no references for uncovered category {category.value}"

    def test_every_returned_doc_id_exists_and_is_tagged_with_the_queried_category(self):
        for raw in SAMPLE_TICKETS:
            ticket = _to_ticket_input(raw)
            category = Category(raw["expected_category"])

            for reference in self.retriever.retrieve(ticket, category):
                assert reference.doc_id in KB_ARTICLES_BY_ID
                article = KB_ARTICLES_BY_ID[reference.doc_id]
                assert category.value in article["category_tags"]
                assert reference.title == article["title"]

    def test_at_least_one_covered_and_one_uncovered_category_are_exercised(self):
        """Sanity check that the fixture set actually exercises both branches (#18 AC)."""
        categories_seen = {Category(raw["expected_category"]) for raw in SAMPLE_TICKETS}
        assert any(category.value in COVERED_CATEGORIES for category in categories_seen)
        assert any(category.value not in COVERED_CATEGORIES for category in categories_seen)


class TestKeywordKBRetrieverDisambiguation:
    """Firmware Update is the only category with more than one candidate KB article
    (KB-WIFI-004, KB-FW-010); these tickets are worded to overlap distinctly with one or
    the other so the deterministic keyword-overlap scoring picks the better match."""

    retriever = KeywordKBRetriever()

    def test_wifi_reconnect_wording_prefers_the_wifi_reconnect_article(self):
        ticket = TicketInput(
            subject="Speaker won't reconnect after update",
            body=(
                "My speaker won't reconnect to Wi-Fi after a firmware update. I've confirmed "
                "my router and network band haven't changed."
            ),
            product_sku="SUM1-ACT",
        )

        references = self.retriever.retrieve(ticket, Category.FIRMWARE_UPDATE)

        assert references[0].doc_id == "KB-WIFI-004"

    def test_stuck_update_wording_prefers_the_firmware_process_article(self):
        ticket = TicketInput(
            subject="Firmware update stuck",
            body=(
                "The firmware update gets stuck partway and fails every time I retry from "
                "settings. I checked the version numbers involved."
            ),
            product_sku="CDR-STRM-MINI",
        )

        references = self.retriever.retrieve(ticket, Category.FIRMWARE_UPDATE)

        assert references[0].doc_id == "KB-FW-010"


class TestKeywordKBRetrieverBehavior:
    def test_no_references_for_uncovered_category(self):
        retriever = KeywordKBRetriever()
        ticket = TicketInput(subject="General question", body="What colors does this come in?")

        references = retriever.retrieve(ticket, Category.GENERAL_QUESTION)

        assert references == []

    def test_max_results_caps_returned_references(self):
        fake_articles = [
            {
                "doc_id": f"KB-FAKE-{i}",
                "title": f"Fake article {i}",
                "type": "faq",
                "category_tags": ["Subwoofer Setup"],
                "product_tags": [],
                "content": "Some subwoofer crossover placement guidance content here.",
            }
            for i in range(5)
        ]
        retriever = KeywordKBRetriever(articles=fake_articles, max_results=2)
        ticket = TicketInput(subject="Subwoofer question", body="Any crossover placement tips?")

        references = retriever.retrieve(ticket, Category.SUBWOOFER_SETUP)

        assert len(references) == 2

    def test_excerpt_is_truncated_for_long_content(self):
        retriever = KeywordKBRetriever()
        ticket = TicketInput(subject="Warranty", body="I want to register my amp for warranty.")

        references = retriever.retrieve(ticket, Category.WARRANTY_REGISTRATION)

        assert references
        assert len(references[0].excerpt) <= 224  # max_len + "..."

    def test_scores_are_deterministic(self):
        retriever = KeywordKBRetriever()
        ticket = TicketInput(subject="Wifi issue", body="My speaker won't reconnect to Wi-Fi.")

        first = retriever.retrieve(ticket, Category.WIFI_NETWORK)
        second = retriever.retrieve(ticket, Category.WIFI_NETWORK)

        assert first == second
