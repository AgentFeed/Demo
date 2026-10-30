from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx

from ..config import settings
from .errors import IntegrationError, IntegrationNotConfigured, IntegrationResponseError


class EmbeddingProvider:
    """384-dimensional embedding provider for pgvector retrieval.

    The preferred local backend is sentence-transformers with the plan's
    MiniLM model. An OpenAI-compatible HTTP endpoint can be selected with
    ``EMBEDDING_API_URL`` for hosted inference.
    """

    def __init__(self) -> None:
        self.backend = settings.embedding_backend
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._model: Any = None
        self.last_error: str | None = None

    @property
    def available(self) -> bool:
        if self.backend == "none":
            return False
        if settings.embedding_api_url:
            return True
        if self.backend != "sentence-transformers":
            return False
        try:
            import sentence_transformers  # type: ignore  # noqa: F401

            return True
        except ImportError:
            return False

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - depends on real install
            self.last_error = "Install sentence-transformers or configure EMBEDDING_API_URL."
            raise IntegrationNotConfigured(self.last_error) from exc
        self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> list[float] | None:
        text = " ".join(str(text or "").split())
        if not text or self.backend == "none":
            return None
        if settings.embedding_api_url:
            headers = {"Authorization": f"Bearer {settings.embedding_api_key}"} if settings.embedding_api_key else {}
            response = httpx.post(settings.embedding_api_url, headers=headers, json={"model": self.model_name, "input": [text]}, timeout=30)
            if response.status_code >= 400:
                raise IntegrationResponseError(f"Embedding endpoint failed with HTTP {response.status_code}.")
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else None
            vector = data[0].get("embedding") if data else None
            if not isinstance(vector, list):
                raise IntegrationResponseError("Embedding endpoint did not return data[0].embedding.")
            return [float(value) for value in vector]
        try:
            vector = self._load_model().encode(text, normalize_embeddings=True)
            values = vector.tolist() if hasattr(vector, "tolist") else list(vector)
            if len(values) != self.dimension:
                raise IntegrationResponseError(f"Expected {self.dimension} embedding values, received {len(values)}.")
            return [float(value) for value in values]
        except IntegrationError:
            raise
        except Exception as exc:  # pragma: no cover - model/runtime dependent
            self.last_error = str(exc)
            raise IntegrationResponseError(f"Embedding generation failed: {exc}") from exc


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    return EmbeddingProvider()
