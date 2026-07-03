"""The LLMClient extension seam. See docs/01_architecture/ARCHITECTURE.md 'Extension seams'.

Every LLM-backed service (classifier, response drafter) depends on this Protocol, never on
the `openai` package directly. This keeps provider swapping and mocking-in-tests possible
without touching service logic. Per .skills/architecture-review.md, no service should
bypass this seam with a direct provider call.
"""

from typing import Protocol

from src.config import settings


class LLMClient(Protocol):
    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Return the model's raw text completion for the given prompts."""
        ...


class MissingAPIKeyError(RuntimeError):
    """Raised when an LLMClient implementation needs an API key that wasn't configured.

    A dedicated subclass (rather than a bare RuntimeError) so callers like
    src/api/main.py's exception handler can catch specifically this configuration problem
    without also silently catching-and-masking an unrelated RuntimeError as if it were one."""


class OpenAILLMClient:
    """Default v0.1 LLMClient implementation, backed by the OpenAI Chat Completions API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key if api_key is not None else settings.openai_api_key
        self._model = model if model is not None else settings.openai_model
        self._client = None  # lazily constructed so importing this module never requires an API key

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            if not self._api_key:
                raise MissingAPIKeyError(
                    "OPENAI_API_KEY is not set. Set it in your environment or .env file "
                    "(see .env.example) before using OpenAILLMClient."
                )
            self._client = OpenAI(api_key=self._api_key)
        return self._client

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""
