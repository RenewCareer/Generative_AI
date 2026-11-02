"""The production layers that wrap a basic RAG pipeline."""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from collections import OrderedDict
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

import numpy as np

from genai_kit import Chunk, Embedder

logger = logging.getLogger("rag.trace")

# ------------------------------------------------------------------ Access control

ROLE_ACCESS = {"customer": {"public"}, "employee": {"public", "internal"}}


def access_filter(role: str):
    """Enforced in the retrieval layer, so forbidden text never reaches the model."""
    if role not in ROLE_ACCESS:
        raise PermissionError(f"Unknown role: {role}")
    allowed = ROLE_ACCESS[role]
    return lambda metadata: metadata.get("access") in allowed


# ------------------------------------------------------------------ Injection screening

INJECTION_PATTERNS = [
    r"ignore (all |any |the |your )?(previous|prior|above)? ?(instructions|rules|prompts?)",
    r"disregard (all |the |your )?(previous|prior|above)? ?(instructions|rules)",
    r"you are now\b",
    r"reveal (your |the )?(system prompt|instructions|credentials|api key)",
    r"(send|forward|email) .{0,40}(to|@)\s*\S+@\S+",
    r"<\s*/?\s*system\s*>",
]
_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.I)


def looks_like_injection(text: str) -> bool:
    """A heuristic filter. It raises the bar, and is one layer among several, not a cure."""
    return bool(_INJECTION_RE.search(text))


def screen_chunks(chunks: list[Chunk]) -> tuple[list[Chunk], list[Chunk]]:
    safe: list[Chunk] = []
    blocked: list[Chunk] = []
    for chunk in chunks:
        (blocked if looks_like_injection(chunk.text) else safe).append(chunk)
    return safe, blocked


# ------------------------------------------------------------------ Semantic cache


@dataclass
class CacheEntry:
    vector: np.ndarray
    answer: dict
    created_at: float


class SemanticCache:
    """Reuses an answer when a new question is close enough to an earlier one.

    Entries are partitioned by scope. Without that, an employee's cached answer about
    internal policy could be served to a customer. The scope includes the index version,
    so that re-indexing automatically invalidates stale answers.
    """

    def __init__(self, embedder: Embedder, threshold: float = 0.92, ttl_s: float = 3600, max_entries: int = 1000):
        self.embedder = embedder
        self.threshold = threshold
        self.ttl_s = ttl_s
        self.max_entries = max_entries
        self._entries: OrderedDict[tuple[str, int], CacheEntry] = OrderedDict()
        self._counter = 0
        self.hits = 0
        self.misses = 0

    def get(self, question: str, scope: str) -> dict | None:
        vector = self.embedder.embed([question])[0]
        now = time.monotonic()
        best_key, best_score = None, self.threshold
        for key, entry in list(self._entries.items()):
            if now - entry.created_at > self.ttl_s:
                del self._entries[key]
            elif key[0] == scope:
                score = float(vector @ entry.vector)
                if score >= best_score:
                    best_key, best_score = key, score
        if best_key is None:
            self.misses += 1
            return None
        self.hits += 1
        self._entries.move_to_end(best_key)
        return self._entries[best_key].answer

    def put(self, question: str, scope: str, answer: dict) -> None:
        self._counter += 1
        vector = self.embedder.embed([question])[0]
        self._entries[(scope, self._counter)] = CacheEntry(vector, answer, time.monotonic())
        while len(self._entries) > self.max_entries:
            self._entries.popitem(last=False)


# ------------------------------------------------------------------ Tracing


@dataclass
class Trace:
    """One record per request: what ran, how long it took, and what it decided."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    spans: list[dict] = field(default_factory=list)
    attributes: dict = field(default_factory=dict)

    @contextmanager
    def span(self, name: str, **attributes) -> Iterator[dict]:
        record = {"name": name, **attributes}
        start = time.perf_counter()
        try:
            yield record
        except Exception as error:
            record["error"] = type(error).__name__
            raise
        finally:
            record["ms"] = round((time.perf_counter() - start) * 1000, 2)
            self.spans.append(record)

    def to_json(self) -> str:
        return json.dumps({"trace_id": self.trace_id, **self.attributes, "spans": self.spans})
