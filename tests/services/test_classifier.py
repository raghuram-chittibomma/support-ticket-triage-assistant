from src.schemas import Category, TicketInput
from src.services.classifier import (
    ClassificationResult,
    classify_ticket,
    rank_categories,
)


class FakeLLMClient:
    """Mocked LLMClient (per #16 AC — unit tests never call OpenAI)."""

    def __init__(self, response: str):
        self.response = response
        self.calls: list[dict] = []

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return self.response


class TestRankCategories:
    def test_wifi_ticket_ranks_wifi_category_highly(self):
        ticket = TicketInput(
            subject="Speakers won't reconnect to Wi-Fi after update",
            body=(
                "My Summit One Active speakers stopped connecting to Wi-Fi right after the "
                "last firmware update. I'm on the 5GHz band."
            ),
            product_sku="SUM1-ACT",
        )

        ranked = rank_categories(ticket)
        top_three = [category for category, _ in ranked[:3]]

        assert Category.WIFI_NETWORK in top_three
        assert len(ranked) == len(Category)

    def test_returns_all_categories_scored(self):
        ticket = TicketInput(subject="Hello", body="Just saying hi, no real issue here.")

        ranked = rank_categories(ticket)

        assert {category for category, _ in ranked} == set(Category)

    def test_scores_are_deterministic(self):
        ticket = TicketInput(subject="Warranty question", body="I want to register my amp for warranty.")

        first = rank_categories(ticket)
        second = rank_categories(ticket)

        assert first == second

    def test_amp_keyword_does_not_match_inside_unrelated_words(self):
        """Regression test (independent Code Reviewer subagent finding on PR #40): "amp" must
        not match inside "sample"/"example", nor "hum" inside "human"."""
        ticket = TicketInput(
            subject="Sample question",
            body="This is just an example of a human interest question, not about any product.",
        )

        ranked = rank_categories(ticket)
        scores_by_category = dict(ranked)

        assert scores_by_category[Category.AMP_SPEAKER_COMPATIBILITY] == 0
        assert scores_by_category[Category.SOUND_QUALITY] == 0

    def test_amp_keyword_still_matches_as_a_standalone_word(self):
        ticket = TicketInput(subject="Amp question", body="Will this amp work with my speakers?")

        ranked = rank_categories(ticket)
        top_three = [category for category, _ in ranked[:3]]

        assert Category.AMP_SPEAKER_COMPATIBILITY in top_three


class TestClassifyTicket:
    def _ticket(self) -> TicketInput:
        return TicketInput(
            subject="Can't pair my DAC over Bluetooth",
            body="I've been trying to pair my AeroDAC 2 over Bluetooth for an hour and it won't pair.",
            product_sku="AERO-DAC2",
        )

    def test_agreement_with_top_pre_filter_candidate_yields_high_confidence(self):
        llm_client = FakeLLMClient(
            response='{"category": "Bluetooth / Pairing", "explanation": "Ticket describes a pairing failure."}'
        )

        result = classify_ticket(self._ticket(), llm_client)

        assert isinstance(result, ClassificationResult)
        assert result.category == Category.BLUETOOTH_PAIRING
        assert result.category_explanation == "Ticket describes a pairing failure."
        assert result.category_confidence == 0.9
        assert len(llm_client.calls) == 1

    def test_llm_override_outside_shortlist_yields_lower_confidence(self):
        llm_client = FakeLLMClient(
            response='{"category": "General Product Question", "explanation": "Actually just a general question."}'
        )

        result = classify_ticket(self._ticket(), llm_client)

        assert result.category == Category.GENERAL_QUESTION
        assert result.category_confidence < 0.9

    def test_malformed_json_falls_back_to_keyword_pre_filter(self):
        llm_client = FakeLLMClient(response="not valid json")

        result = classify_ticket(self._ticket(), llm_client)

        assert result.category == Category.BLUETOOTH_PAIRING
        assert "falling back" in result.category_explanation.lower()

    def test_unknown_category_string_falls_back_to_keyword_pre_filter(self):
        llm_client = FakeLLMClient(response='{"category": "Not A Real Category", "explanation": "oops"}')

        result = classify_ticket(self._ticket(), llm_client)

        assert result.category == Category.BLUETOOTH_PAIRING
        assert "falling back" in result.category_explanation.lower()

    def test_missing_explanation_gets_a_default(self):
        llm_client = FakeLLMClient(response='{"category": "Bluetooth / Pairing"}')

        result = classify_ticket(self._ticket(), llm_client)

        assert result.category == Category.BLUETOOTH_PAIRING
        assert result.category_explanation == "Classified as Bluetooth / Pairing."

    def test_markdown_fenced_json_response_is_parsed(self):
        llm_client = FakeLLMClient(
            response='```json\n{"category": "Bluetooth / Pairing", "explanation": "Pairing failure."}\n```'
        )

        result = classify_ticket(self._ticket(), llm_client)

        assert result.category == Category.BLUETOOTH_PAIRING
        assert result.category_explanation == "Pairing failure."

    def test_prompt_includes_ticket_subject_and_body(self):
        llm_client = FakeLLMClient(
            response='{"category": "Bluetooth / Pairing", "explanation": "ok"}'
        )
        ticket = self._ticket()

        classify_ticket(ticket, llm_client)

        user_prompt = llm_client.calls[0]["user_prompt"]
        assert ticket.subject in user_prompt
        assert ticket.body in user_prompt
