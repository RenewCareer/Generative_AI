"""
Intermediate example: NumPy and pandas patterns used throughout AI work.

Requires: numpy, pandas (see requirements.txt).

Part 1 (NumPy) previews a concept sub-topic 1.4 covers in full: text
"meaning" can be represented as a vector of numbers (an embedding), and
comparing meaning becomes comparing vectors mathematically. We use tiny
hand-made 3-number vectors here, not real embeddings, purely to build
comfort with vector operations before 1.4 makes it rigorous.

Part 2 (pandas) covers filtering, grouping, and joining -- the operations
you'll run on every dataset you touch in this curriculum.

Run it with:
    python 02_intermediate_numpy_pandas_for_ai.py
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Part 1: NumPy -- vectors are the currency of AI/ML.
# ---------------------------------------------------------------------------
def demo_numpy_vectors() -> None:
    print("=" * 70)
    print("NumPy: vectors as a stand-in for 'meaning' (a preview of 1.4)")
    print("=" * 70)

    # Pretend these are toy 3-dimensional "embeddings" for three short
    # phrases, where each dimension loosely represents some latent concept
    # (this is NOT how real embeddings are built -- it's a hand-picked
    # illustration so the numbers are easy to reason about).
    embeddings = {
        "dog":  np.array([0.9, 0.1, 0.0]),
        "puppy": np.array([0.85, 0.15, 0.05]),
        "car":  np.array([0.0, 0.1, 0.95]),
    }

    for word, vec in embeddings.items():
        print(f"  {word!r:8s} -> {vec}")

    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    print("\nCosine similarity (1.0 = identical direction, 0.0 = unrelated):")
    print(f"  dog vs puppy: {cosine_similarity(embeddings['dog'], embeddings['puppy']):.3f}")
    print(f"  dog vs car:   {cosine_similarity(embeddings['dog'], embeddings['car']):.3f}")
    print(
        "\n'dog' and 'puppy' point in a similar direction (high similarity);"
        "\n'dog' and 'car' don't. This is the exact math vector databases use"
        "\nto find 'similar' documents in Track 3 -- just with 1000+ dimensional"
        "\nvectors produced by a real embedding model instead of 3 hand-picked ones."
    )

    # Vectorized operations -- no Python for-loop needed.
    stacked = np.stack(list(embeddings.values()))
    print(f"\nAll embeddings stacked into a matrix, shape={stacked.shape}")
    print(f"Column-wise mean (average value per dimension): {stacked.mean(axis=0)}")


# ---------------------------------------------------------------------------
# Part 2: pandas -- filter, group, join. The bread and butter of working
# with any tabular dataset (which is most of what you'll do outside of
# raw text).
# ---------------------------------------------------------------------------
def demo_pandas_operations() -> None:
    print("\n" + "=" * 70)
    print("pandas: filter, group, join")
    print("=" * 70)

    docs = pd.DataFrame({
        "doc_id": [1, 2, 3, 4, 5],
        "title": ["Intro to AI", "Deep Learning Basics", "Prompt Engineering 101",
                   "RAG Systems", "Vector Databases"],
        "category": ["foundations", "foundations", "prompting", "applications", "applications"],
        "word_count": [1200, 2100, 900, 1800, 1500],
    })

    ratings = pd.DataFrame({
        "doc_id": [1, 2, 3, 4, 5],
        "avg_rating": [4.2, 4.7, 4.9, 4.5, 4.1],
    })

    print("Documents:")
    print(docs.to_string(index=False))

    print("\nFilter: documents with word_count > 1300")
    print(docs[docs["word_count"] > 1300].to_string(index=False))

    print("\nGroup by category: average word count")
    print(docs.groupby("category")["word_count"].mean().to_string())

    print("\nJoin documents with their ratings (on doc_id)")
    merged = docs.merge(ratings, on="doc_id")
    print(merged.to_string(index=False))

    print("\nVectorized column math (no for-loop): a 'quality score' column")
    merged["quality_score"] = (merged["avg_rating"] / 5) * 100
    print(merged[["title", "avg_rating", "quality_score"]].to_string(index=False))


def main() -> None:
    demo_numpy_vectors()
    demo_pandas_operations()


if __name__ == "__main__":
    main()
