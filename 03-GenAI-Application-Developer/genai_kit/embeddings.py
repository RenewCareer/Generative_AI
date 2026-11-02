"""Text embeddings: real ones via OpenAI, plus an offline stand-in."""

from __future__ import annotations

import hashlib
from typing import Protocol

import numpy as np

from genai_kit.config import get_settings
from genai_kit.text import analyze


class Embedder(Protocol):
    name: str

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return one L2-normalised row per input text."""
        ...


def _normalise(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


class HashingEmbedder:
    """Offline embedder using the hashing trick over word uni-grams and bi-grams.

    It captures shared WORDS, not MEANING: "car" and "automobile" are unrelated here.
    That is enough to demonstrate the mechanics in class, and the gap against real
    embeddings is itself a useful teaching point.
    """

    name = "hashing-offline"

    def __init__(self, dim: int = 1024) -> None:
        self.dim = dim

    def _bucket(self, token: str) -> tuple[int, float]:
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        value = int.from_bytes(digest, "little")
        return value % self.dim, 1.0 if value >> 63 else -1.0

    def embed(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            words = analyze(text)
            for token in words + [f"{a} {b}" for a, b in zip(words, words[1:])]:
                column, sign = self._bucket(token)
                matrix[row, column] += sign
        return _normalise(matrix)


class OpenAIEmbedder:
    def __init__(self, model: str | None = None, batch_size: int = 128) -> None:
        from openai import OpenAI

        settings = get_settings()
        self.name = model or settings.openai_embedding_model
        self.batch_size = batch_size
        self._client = OpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_s)

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            response = self._client.embeddings.create(
                model=self.name, input=texts[start : start + self.batch_size]
            )
            vectors.extend(item.embedding for item in response.data)
        return _normalise(np.asarray(vectors, dtype=np.float32))


def get_embedder() -> Embedder:
    """OpenAI embeddings whenever a key exists; otherwise the offline stand-in.

    Anthropic does not offer an embeddings endpoint, so Claude users stay offline here
    unless they also set OPENAI_API_KEY.
    """
    if get_settings().openai_api_key and get_settings().provider != "mock":
        return OpenAIEmbedder()
    return HashingEmbedder()
