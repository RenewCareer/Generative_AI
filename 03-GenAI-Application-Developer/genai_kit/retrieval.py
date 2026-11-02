"""Chunking, vector search, keyword search and fusion, built up in modules 03/02 to 03/05."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genai_kit.config import COURSE_DATA
from genai_kit.embeddings import Embedder, HashingEmbedder
from genai_kit.text import analyze


@dataclass
class Chunk:
    id: str
    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    chunk: Chunk
    score: float


def parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    """Split ``--- key: value ---`` front matter from a Markdown body."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not match:
        return {}, raw
    metadata = dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)
    return metadata, match.group(2).strip()


def load_course_docs() -> list[dict[str, Any]]:
    """Load the fictional Acme Retail knowledge base shipped in course_data/docs."""
    docs = []
    for path in sorted((COURSE_DATA / "docs").glob("*.md")):
        metadata, body = parse_front_matter(path.read_text(encoding="utf-8"))
        docs.append({"doc_id": path.stem, "text": body, "metadata": metadata})
    return docs


def recursive_chunk(
    text: str,
    max_chars: int = 500,
    overlap: int = 60,
    separators: tuple[str, ...] = ("\n## ", "\n\n", "\n", ". ", " "),
) -> list[str]:
    """Split on the largest natural boundary that fits, then merge with overlap."""

    def split(piece: str, level: int) -> list[str]:
        if len(piece) <= max_chars:
            return [piece]
        if level == len(separators):
            return [piece[i : i + max_chars] for i in range(0, len(piece), max_chars)]
        separator = separators[level]
        parts = piece.split(separator)
        pieces: list[str] = []
        for index, part in enumerate(parts):
            # Keep the separator with the text it introduces.
            restored = (separator.lstrip("\n") if separator.startswith("\n#") else "") + part
            if index == 0:
                restored = part
            if restored.strip():
                pieces.extend(split(restored, level + 1))
        return pieces

    chunks: list[str] = []
    current = ""
    for piece in split(text.strip(), 0):
        if current and len(current) + len(piece) + 2 > max_chars:
            chunks.append(current.strip())
            current = current[-overlap:].lstrip() + " " if overlap else ""
        current += piece.strip() + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def load_course_chunks(max_chars: int = 300, overlap: int = 40) -> list[Chunk]:
    """Chunk the knowledge base, prefixing each chunk with its document title."""
    chunks = []
    for doc in load_course_docs():
        title = doc["metadata"].get("title", doc["doc_id"])
        for number, text in enumerate(recursive_chunk(doc["text"], max_chars, overlap)):
            chunks.append(Chunk(f"{doc['doc_id']}#{number}", doc["doc_id"], f"{title}\n{text}", dict(doc["metadata"])))
    return chunks


MetadataFilter = Callable[[dict[str, Any]], bool]


class VectorIndex:
    """Exact (brute force) cosine search. Good to about 100k vectors, and easy to read."""

    def __init__(self, embedder: Embedder | None = None) -> None:
        self.embedder = embedder or HashingEmbedder()
        self.chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None

    def add(self, chunks: Iterable[Chunk]) -> "VectorIndex":
        new = list(chunks)
        if not new:
            return self
        vectors = self.embedder.embed([chunk.text for chunk in new])
        self._matrix = vectors if self._matrix is None else np.vstack([self._matrix, vectors])
        self.chunks.extend(new)
        return self

    def search(self, query: str, k: int = 5, where: MetadataFilter | None = None) -> list[SearchHit]:
        if self._matrix is None:
            return []
        scores = self._matrix @ self.embedder.embed([query])[0]
        order = np.argsort(-scores)
        hits: list[SearchHit] = []
        for index in order:
            chunk = self.chunks[int(index)]
            if where is None or where(chunk.metadata):
                hits.append(SearchHit(chunk, float(scores[index])))
                if len(hits) == k:
                    break
        return hits


class BM25Index:
    """Okapi BM25 keyword search. Finds exact terms such as error codes and SKUs."""

    def __init__(self, chunks: Iterable[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = list(chunks)
        self.k1, self.b = k1, b
        self._docs = [Counter(self._tokens(chunk.text)) for chunk in self.chunks]
        self._lengths = [sum(doc.values()) for doc in self._docs]
        self._average = sum(self._lengths) / max(len(self._lengths), 1)
        frequency = Counter(term for doc in self._docs for term in doc)
        total = len(self._docs)
        self._idf = {
            term: math.log(1 + (total - count + 0.5) / (count + 0.5)) for term, count in frequency.items()
        }

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return analyze(text, pattern=r"[a-z0-9-]+")

    def search(self, query: str, k: int = 5, where: MetadataFilter | None = None) -> list[SearchHit]:
        terms = self._tokens(query)
        hits = []
        for doc, length, chunk in zip(self._docs, self._lengths, self.chunks):
            if where is not None and not where(chunk.metadata):
                continue
            score = 0.0
            for term in terms:
                tf = doc.get(term, 0)
                if tf:
                    denominator = tf + self.k1 * (1 - self.b + self.b * length / self._average)
                    score += self._idf[term] * tf * (self.k1 + 1) / denominator
            if score > 0:
                hits.append(SearchHit(chunk, score))
        return sorted(hits, key=lambda hit: -hit.score)[:k]


def reciprocal_rank_fusion(rankings: list[list[SearchHit]], k: int = 5, c: int = 60) -> list[SearchHit]:
    """Merge ranked lists using ranks only, so the score scales need not match."""
    scores: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for ranking in rankings:
        for rank, hit in enumerate(ranking, start=1):
            scores[hit.chunk.id] = scores.get(hit.chunk.id, 0.0) + 1 / (c + rank)
            chunks[hit.chunk.id] = hit.chunk
    ordered = sorted(scores, key=lambda chunk_id: -scores[chunk_id])[:k]
    return [SearchHit(chunks[chunk_id], scores[chunk_id]) for chunk_id in ordered]


def format_context(hits: list[SearchHit]) -> str:
    """Number each source so that the model can cite [1], [2], ..."""
    return "\n".join(
        f"[{number}] (source: {hit.chunk.doc_id})\n{hit.chunk.text}" for number, hit in enumerate(hits, start=1)
    )


def load_golden(name: str = "golden_questions.jsonl") -> list[dict[str, Any]]:
    path = COURSE_DATA / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
