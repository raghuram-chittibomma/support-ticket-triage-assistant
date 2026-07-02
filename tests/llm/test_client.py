from unittest.mock import MagicMock, patch

import pytest

from src.llm.client import OpenAILLMClient


class TestOpenAILLMClient:
    def test_raises_clear_error_without_api_key(self):
        client = OpenAILLMClient(api_key="", model="gpt-4o-mini")

        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            client.complete(system_prompt="sys", user_prompt="user")

    def test_complete_sends_expected_request_and_returns_content(self):
        fake_response = MagicMock()
        fake_response.choices = [MagicMock(message=MagicMock(content="hello there"))]

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = fake_response
            mock_openai_cls.return_value = mock_client

            client = OpenAILLMClient(api_key="fake-key", model="gpt-4o-mini")
            result = client.complete(system_prompt="You are helpful.", user_prompt="Hi")

        assert result == "hello there"
        mock_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-4o-mini"
        assert kwargs["messages"] == [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ]

    def test_client_is_constructed_lazily_and_reused(self):
        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="x"))]
            )
            mock_openai_cls.return_value = mock_client

            client = OpenAILLMClient(api_key="fake-key")
            client.complete(system_prompt="a", user_prompt="b")
            client.complete(system_prompt="c", user_prompt="d")

        mock_openai_cls.assert_called_once()
