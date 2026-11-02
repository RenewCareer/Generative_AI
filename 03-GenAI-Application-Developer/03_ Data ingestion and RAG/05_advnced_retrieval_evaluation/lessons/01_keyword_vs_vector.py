"""Lesson 1: keyword and vector search fail in different ways, which is why we combine them.

Run: python lessons/01_keyword_vs_vector.py
"""

from genai_kit import BM25Index, VectorIndex, get_embedder, load_course_chunks, reciprocal_rank_fusion

QUERIES = ["SHP-404", "can I swim with my fitness band", "gift card money back"]


def top(hits, count=3) -> str:
    return ", ".join(hit.chunk.id for hit in hits[:count]) or "(nothing)"


def main() -> None:
    chunks = load_course_chunks()
    vector = VectorIndex(get_embedder()).add(chunks)
    keyword = BM25Index(chunks)

    for query in QUERIES:
        vector_hits, keyword_hits = vector.search(query, k=10), keyword.search(query, k=10)
        print(f"Query: {query}")
        print(f"  vector : {top(vector_hits)}")
        print(f"  bm25   : {top(keyword_hits)}")
        print(f"  hybrid : {top(reciprocal_rank_fusion([vector_hits, keyword_hits]))}\n")

    print("How reciprocal rank fusion scores a document found at rank 1 and rank 3 (c=60):")
    print(f"  1/(60+1) + 1/(60+3) = {1 / 61 + 1 / 63:.4f}")
    print("It uses only ranks, so BM25's and cosine's different score scales do not matter.")


if __name__ == "__main__":
    main()
