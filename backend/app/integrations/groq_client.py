from __future__ import annotations

import json
from typing import Any

from ..config import settings
from .errors import IntegrationNotConfigured, IntegrationResponseError


class GroqJsonClient:
    """Small Groq adapter for structured resume/coach responses.

    Groq supports JSON Object Mode across the models used by the plan. The
    model remains configurable so a deployment can move to a newer model
    without changing application code.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self._client: Any = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self) -> Any:
        if not self.available:
            raise IntegrationNotConfigured("Set GROQ_API_KEY to enable Groq-backed agents.")
        if self._client is None:
            try:
                from groq import Groq
            except ImportError as exc:  # pragma: no cover - depends on real install
                raise IntegrationNotConfigured("Install the groq package for Groq-backed agents.") from exc
            self._client = Groq(api_key=self.api_key)
        return self._client

    def json_completion(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.1,
        max_tokens: int = 1600,
    ) -> dict[str, Any]:
        response = self._get_client().chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise IntegrationResponseError("Groq returned an empty completion.")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise IntegrationResponseError("Groq returned invalid JSON.") from exc
        if not isinstance(parsed, dict):
            raise IntegrationResponseError("Groq JSON response must be an object.")
        return parsed


_client: GroqJsonClient | None = None


def get_groq_client() -> GroqJsonClient | None:
    global _client
    if not settings.groq_api_key:
        return None
    if _client is None:
        _client = GroqJsonClient()
    return _client
