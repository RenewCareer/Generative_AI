import pytest

from genai_kit import BM25Index, Chunk, MockClient, VectorIndex, load_course_chunks
from project.benchmark import HARD_QUESTIONS, build_retrievers, evaluate
from project.metrics import contains_all, groundedness, hit_at_k, ndcg_at_k, reciprocal_rank
from project.retrievers import (
    hybrid_retriever,
    multi_query_retriever,
    overlap_rerank_score,
    reranked_retriever,
    rewrite_query,
    vector_retriever,
)


def test_ranking_metrics():
    retrieved = ["x", "y", "target"]
    assert hit_at_k(retrieved, "target", 2) == 0
    assert hit_at_k(retrieved, "target", 3) == 1
    assert reciprocal_rank(retrieved, "target") == pytest.approx(1 / 3)
    assert ndcg_at_k(["target", "x"], "target", 2) == pytest.approx(1.0)
    assert ndcg_at_k(retrieved, "target", 3) == pytest.approx(0.5)
    assert ndcg_at_k(["x"], "target", 1) == 0


def test_groundedness_flags_invented_sentences():
    context = "Hotel stays are reimbursed up to 180 dollars per night."
    assert groundedness("Hotel stays are reimbursed up to 180 dollars per night [1].", context) == 1.0
    assert groundedness("Hotel stays are reimbursed. Pets stay free on weekends.", context) == 0.5
    assert groundedness("", context) == 0.0


def test_contains_all_is_case_insensitive():
    assert contains_all("Up to 180 Dollars", ["180 dollars"]) == 1.0
    assert contains_all("Up to 200 dollars", ["180 dollars"]) == 0.0


def test_bm25_finds_exact_code_that_vector_may_not_rank_first():
    keyword = BM25Index(load_course_chunks())
    assert keyword.search("NB-17", k=1)[0].chunk.doc_id == "product_faq"


def test_reranker_prefers_terms_close_together():
    near = Chunk("a", "a", "the hotel limit is high " + "word " * 40)
    far = Chunk("b", "b", "hotel " + "word " * 40 + " limit")
    assert overlap_rerank_score("hotel limit", near) > overlap_rerank_score("hotel limit", far)


def test_rerank_returns_requested_count():
    chunks = load_course_chunks()
    hybrid = hybrid_retriever(VectorIndex().add(chunks), BM25Index(chunks))
    assert len(reranked_retriever(hybrid)("hotel limit", 3)) == 3


def test_rewrite_keeps_original_and_limits_count():
    llm = MockClient(lambda messages, system, tools: "a\nb\nc\nd\ne")
    assert rewrite_query(llm, "original") == ["original", "a", "b", "c"]


def test_multi_query_merges_results():
    chunks = load_course_chunks()
    retriever = multi_query_retriever(
        vector_retriever(VectorIndex().add(chunks)),
        MockClient(lambda messages, system, tools: "refund policy return window"),
    )
    assert any(hit.chunk.doc_id == "refund_policy" for hit in retriever("I want my money back", 5))


def test_benchmark_produces_sane_scores():
    results = {name: evaluate(retriever, HARD_QUESTIONS) for name, retriever in build_retrievers().items()}
    for scores in results.values():
        assert all(0 <= value <= 1 for value in scores.values())
    # Keyword search must solve the exact-code queries that motivate hybrid search.
    assert results["bm25"]["hit@5"] >= 0.8
