"""Lesson 2: two-stage retrieval (rerank) and query rewriting.

Offline, the reranker is a term-proximity heuristic and rewrites are scripted, so that the
flow is visible. In production: a cross-encoder or rerank API, and a real model for rewrites.

Run: python lessons/02_rerank_and_query_rewrite.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import BM25Index, VectorIndex, get_embedder, get_llm, load_course_chunks  # noqa: E402
from project.retrievers import (  # noqa: E402
    hybrid_retriever,
    multi_query_retriever,
    reranked_retriever,
    rewrite_query,
)


def scripted_rewrites(messages, system, tools) -> str:
    """Stand-in for the model: what a good rewrite of this question would look like."""
    return "refund for returned items\nreturn window policy\nhow refunds are paid"


def main() -> None:
    chunks = load_course_chunks()
    first_stage = hybrid_retriever(VectorIndex(get_embedder()).add(chunks), BM25Index(chunks))

    question = "ticket response target priority 1"
    print(f"RERANKING: {question}")
    print("  first stage:", [hit.chunk.id for hit in first_stage(question, 3)])
    print("  reranked   :", [hit.chunk.id for hit in reranked_retriever(first_stage)(question, 3)])

    question = "I changed my mind about a purchase, can I get my money back?"
    llm = get_llm(mock_handler=scripted_rewrites)
    print(f"\nQUERY REWRITING: {question}")
    for query in rewrite_query(llm, question):
        print(f"  - {query}")
    print("  single query:", [hit.chunk.id for hit in first_stage(question, 3)])
    print("  multi query :", [hit.chunk.id for hit in multi_query_retriever(first_stage, llm)(question, 3)])

    print("\nEach step adds latency and cost. Add one only if your benchmark shows that it helps.")


if __name__ == "__main__":
    main()
