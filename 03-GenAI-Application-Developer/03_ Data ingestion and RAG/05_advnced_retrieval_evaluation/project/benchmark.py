"""Example application: Retrieval Benchmark, choosing a retriever using evidence.

Runs each strategy over the golden questions and a harder set, then writes a Markdown report.

Run: python project/benchmark.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from statistics import mean

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from genai_kit import BM25Index, VectorIndex, get_embedder, load_course_chunks  # noqa: E402
from genai_kit.retrieval import load_golden  # noqa: E402
from project.metrics import contains_all, hit_at_k, ndcg_at_k, reciprocal_rank  # noqa: E402
from project.retrievers import (  # noqa: E402
    Retriever,
    bm25_retriever,
    hybrid_retriever,
    reranked_retriever,
    vector_retriever,
)

# Terse, keyword-like, or differently worded queries, as real users type them.
HARD_QUESTIONS = [
    {"question": "SHP-404", "doc_id": "shipping_policy", "must_include": ["SHP-404"]},
    {"question": "NB-17", "doc_id": "product_faq", "must_include": ["NB-17"]},
    {"question": "gift card money back", "doc_id": "refund_policy", "must_include": ["gift cards"]},
    {"question": "reset speaker", "doc_id": "product_faq", "must_include": ["15 seconds"]},
    {"question": "sick note rules", "doc_id": "leave_policy", "must_include": ["doctor"]},
    {"question": "business class flights", "doc_id": "expense_policy", "must_include": ["8 hours"]},
    {"question": "customs fees abroad", "doc_id": "shipping_policy", "must_include": ["Customs"]},
    {"question": "can I swim with my fitness band", "doc_id": "product_faq", "must_include": ["50 metres"]},
    {"question": "free delivery threshold", "doc_id": "shipping_policy", "must_include": ["75 dollars"]},
    {"question": "ticket response target priority 1", "doc_id": "support_handbook", "must_include": ["1 hour"]},
]

# The words differ from the documents. Lexical search should struggle here, and real
# embeddings should do better. This set is the one to rerun once you add an API key.
PARAPHRASED_QUESTIONS = [
    {"question": "I changed my mind, how do I get my money back", "doc_id": "refund_policy", "must_include": ["30 days"]},
    {"question": "time off after having a baby", "doc_id": "leave_policy", "must_include": ["16 weeks"]},
    {"question": "my order has not moved for days", "doc_id": "shipping_policy", "must_include": ["SHP-404"]},
    {"question": "someone hacked my account, who do I tell", "doc_id": "security_policy", "must_include": ["security@acme"]},
    {"question": "the charger stopped working after six weeks", "doc_id": "warranty", "must_include": ["6 month"]},
    {"question": "can I claim a glass of wine with dinner", "doc_id": "expense_policy", "must_include": ["Alcohol"]},
    {"question": "smart speaker cannot reach the internet", "doc_id": "product_faq", "must_include": ["Wi-Fi"]},
    {"question": "customer is threatening to sue us", "doc_id": "support_handbook", "must_include": ["legal"]},
]


def evaluate(retriever: Retriever, questions: list[dict], k: int = 5) -> dict[str, float]:
    rows = []
    for item in questions:
        hits = retriever(item["question"], k)
        documents = [hit.chunk.doc_id for hit in hits]
        text = " ".join(hit.chunk.text for hit in hits[:3])
        rows.append(
            {
                "hit@1": hit_at_k(documents, item["doc_id"], 1),
                "hit@5": hit_at_k(documents, item["doc_id"], 5),
                "mrr": reciprocal_rank(documents, item["doc_id"]),
                "ndcg@5": ndcg_at_k(documents, item["doc_id"], 5),
                "answer@3": contains_all(text, item["must_include"]),
            }
        )
    return {metric: mean(row[metric] for row in rows) for metric in rows[0]}


def build_retrievers() -> dict[str, Retriever]:
    chunks = load_course_chunks()
    vector = VectorIndex(get_embedder()).add(chunks)
    keyword = BM25Index(chunks)
    hybrid = hybrid_retriever(vector, keyword)
    return {
        "vector": vector_retriever(vector),
        "bm25": bm25_retriever(keyword),
        "hybrid (RRF)": hybrid,
        "hybrid + rerank": reranked_retriever(hybrid),
    }


def to_markdown(title: str, results: dict[str, dict[str, float]]) -> str:
    metrics = list(next(iter(results.values())))
    lines = [f"### {title}", "", "| retriever | " + " | ".join(metrics) + " |", "|---|" + "---|" * len(metrics)]
    for name, scores in results.items():
        lines.append(f"| {name} | " + " | ".join(f"{scores[metric]:.2f}" for metric in metrics) + " |")
    return "\n".join(lines)


def main() -> None:
    embedder_name = get_embedder().name
    retrievers = build_retrievers()
    sections = [f"# Retrieval benchmark\n\nEmbedder: `{embedder_name}`"]
    for title, questions in (
        (f"Golden questions ({len(load_golden())})", load_golden()),
        (f"Hard questions ({len(HARD_QUESTIONS)})", HARD_QUESTIONS),
        (f"Paraphrased questions ({len(PARAPHRASED_QUESTIONS)})", PARAPHRASED_QUESTIONS),
    ):
        results = {name: evaluate(retriever, questions) for name, retriever in retrievers.items()}
        sections.append(to_markdown(title, results))

    report = "\n\n".join(sections) + "\n"
    print(report)
    output = UNIT / "output" / "benchmark_report.md"
    output.parent.mkdir(exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
