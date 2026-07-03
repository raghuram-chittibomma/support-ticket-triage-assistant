"""Integration tests for the FastAPI service. See #23's acceptance criteria and
.skills/fastapi-service-review.md. The real OpenAI call is faked by patching
`OpenAILLMClient` where `run_triage_pipeline` looks it up (`src.workflows.triage_pipeline`),
so these tests make no network calls — only the HTTP layer + full pipeline wiring is
exercised, matching how `tests/workflows/test_triage_pipeline.py` fakes the LLM.
"""

import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.llm import OpenAILLMClient
from src.schemas import Category, TriageResult

client = TestClient(app)


class ScriptedLLMClient:
    """See tests/workflows/test_triage_pipeline.py::ScriptedLLMClient — same approach,
    duplicated here since API tests patch the class constructor rather than injecting an
    instance directly (the API doesn't accept an `llm_client` parameter over HTTP)."""

    def __init__(self, expected_category: Category):
        self.expected_category = expected_category

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        if "Choose exactly one category" in system_prompt:
            return json.dumps(
                {
                    "category": self.expected_category.value,
                    "explanation": f"This matches the {self.expected_category.value} category.",
                }
            )
        return json.dumps(
            {
                "likely_issue": "The customer is experiencing the issue described in the ticket body.",
                "suggested_next_action": "Review the ticket details and respond with tailored guidance.",
                "suggested_response": "Thanks for reaching out — we're looking into this for you.",
            }
        )


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestTriageEndpointSuccess:
    def test_triage_returns_a_complete_result(self):
        with patch(
            "src.workflows.triage_pipeline.OpenAILLMClient",
            return_value=ScriptedLLMClient(Category.WIFI_NETWORK),
        ):
            response = client.post(
                "/triage",
                json={
                    "subject": "Speaker won't reconnect to Wi-Fi",
                    "body": "My speaker stopped reconnecting to Wi-Fi after the last firmware update.",
                    "product_sku": "SUM1-ACT",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == Category.WIFI_NETWORK.value
        assert data["likely_issue"]
        assert data["suggested_next_action"]
        assert data["suggested_response"]
        assert isinstance(data["references"], list)
        assert data["confidence_level"] in ("high", "medium", "low")
        assert isinstance(data["human_review_required"], bool)

    def test_triage_response_validates_against_triage_result_schema(self):
        with patch(
            "src.workflows.triage_pipeline.OpenAILLMClient",
            return_value=ScriptedLLMClient(Category.GENERAL_QUESTION),
        ):
            response = client.post(
                "/triage",
                json={"subject": "Quick question", "body": "What colors do you offer for the Summit One?"},
            )

        assert response.status_code == 200
        TriageResult.model_validate(response.json())

    def test_generated_ticket_id_not_required_in_request(self):
        with patch(
            "src.workflows.triage_pipeline.OpenAILLMClient",
            return_value=ScriptedLLMClient(Category.GENERAL_QUESTION),
        ):
            response = client.post("/triage", json={"subject": "Hi", "body": "Just a general question."})

        assert response.status_code == 200


class TestTriageEndpointValidation:
    """Malformed input never reaches pipeline code — FastAPI/Pydantic short-circuits to a
    422 before the (patched or real) LLMClient would ever be called."""

    def test_missing_required_field_returns_422(self):
        response = client.post("/triage", json={"subject": "Missing body"})

        assert response.status_code == 422

    def test_empty_subject_returns_422(self):
        response = client.post("/triage", json={"subject": "", "body": "Some body text."})

        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post("/triage", json={"subject": "Some subject", "body": ""})

        assert response.status_code == 422

    def test_invalid_channel_value_returns_422(self):
        response = client.post(
            "/triage", json={"subject": "S", "body": "B", "channel": "carrier-pigeon"}
        )

        assert response.status_code == 422

    def test_malformed_json_body_returns_422(self):
        response = client.post(
            "/triage", content="not valid json", headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_missing_body_entirely_returns_422(self):
        response = client.post("/triage")

        assert response.status_code == 422


class TestTriageEndpointErrorHandling:
    def test_missing_api_key_returns_clear_500_not_a_raw_traceback(self):
        with patch(
            "src.workflows.triage_pipeline.OpenAILLMClient",
            return_value=OpenAILLMClient(api_key=""),
        ):
            response = client.post("/triage", json={"subject": "S", "body": "B"})

        assert response.status_code == 500
        assert "OPENAI_API_KEY" in response.json()["detail"]
