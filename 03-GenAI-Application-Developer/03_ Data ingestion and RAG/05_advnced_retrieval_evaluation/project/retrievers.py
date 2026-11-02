"""Retrieval strategies behind one signature: (question, k) -> ranked hits."""

from __future__ import annotations

from collections.abc import Callable

from genai_kit import (
    BM25Index,
    Chunk,
    LLMClient,
    SearchHit,
    VectorIndex,
    reciprocal_rank_fusion,
)
from genai_kit.text import analyze

Retriever = Callable[[str, int], list[SearchHit]]
CANDIDATES = 20


def vector_retriever(index: VectorIndex) -> Retriever:
    return lambda question, k: index.search(question, k=k)


def bm25_retriever(index: BM25Index) -> Retriever:
    return lambda question, k: index.search(question, k=k)


def hybrid_retriever(vector: VectorIndex, keyword: BM25Index) -> Retriever:
    """Run both searches and merge with reciprocal rank fusion."""

    def retrieve(question: str, k: int) -> list[SearchHit]:
        return reciprocal_rank_fusion(
            [vector.search(question, k=CANDIDATES), keyword.search(question, k=CANDIDATES)], k=k
        )

    return retrieve


def overlap_rerank_score(question: str, chunk: Chunk) -> float:
    """Offline stand-in for a cross-encoder: rewards question terms appearing close together."""
    terms = set(analyze(question, pattern=r"[a-z0-9-]+"))
    words = analyze(chunk.text, pattern=r"[a-z0-9-]+")
    if not terms or not words:
        return 0.0
    best = 0
    window = 15
    for start in range(max(1, len(words) - window + 1)):
        best = max(best, len(terms & set(words[start : start + window])))
    return best / len(terms)


def reranked_retriever(
    first_stage: Retriever,
    score: Callable[[str, Chunk], float] = overlap_rerank_score,
) -> Retriever:
    """Fetch many candidates cheaply, then rescore them with a slower, sharper model."""

    def retrieve(question: str, k: int) -> list[SearchHit]:
        candidates = first_stage(question, CANDIDATES)
        rescored = [SearchHit(hit.chunk, score(question, hit.chunk)) for hit in candidates]
        return sorted(rescored, key=lambda hit: -hit.score)[:k]

    return retrieve


def rewrite_query(llm: LLMClient, question: str, count: int = 3) -> list[str]:
    """Ask the model for alternative phrasings, to bridge the vocabulary gap."""
    response = llm.complete(
        [{"role": "user", "content": question}],
        system=(
            f"Rewrite the user's question as {count} different search queries for a company "
            "policy knowledge base, using likely policy vocabulary. Return one query per line, "
            "and nothing else."
        ),
        max_tokens=150,
    )
    queries = [line.strip(" -\t") for line in response.text.splitlines() if line.strip()]
    return [question, *queries[:count]]


def multi_query_retriever(first_stage: Retriever, llm: LLMClient) -> Retriever:
    def retrieve(question: str, k: int) -> list[SearchHit]:
        rankings = [first_stage(query, CANDIDATES) for query in rewrite_query(llm, question)]
        return reciprocal_rank_fusion(rankings, k=k)

    return retrieve
