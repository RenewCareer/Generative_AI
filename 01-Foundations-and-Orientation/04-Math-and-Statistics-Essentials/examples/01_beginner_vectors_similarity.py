"""
Beginner example: dot product, vector magnitude, and cosine similarity --
implemented by hand, then cross-checked with NumPy.

Requires: numpy (see requirements.txt).

The point of implementing these by hand first is to prove there is no
hidden magic: NumPy is just a fast, correct implementation of the exact
same formulas you can write yourself in a few lines.

Run it with:
    python 01_beginner_vectors_similarity.py
"""

import math

import numpy as np


# ---------------------------------------------------------------------------
# Pure-Python implementations (no libraries) -- so you see every operation.
# ---------------------------------------------------------------------------
def dot_product_by_hand(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def magnitude_by_hand(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity_by_hand(a: list[float], b: list[float]) -> float:
    return dot_product_by_hand(a, b) / (magnitude_by_hand(a) * magnitude_by_hand(b))


# ---------------------------------------------------------------------------
# NumPy implementations -- same math, vectorized and fast.
# ---------------------------------------------------------------------------
def cosine_similarity_numpy(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    # Three toy "embeddings" -- same idea as sub-topic 1.3's preview, but
    # now we compute similarity two different ways and PROVE they agree.
    vectors = {
        "cat":       [0.9, 0.2, 0.1, 0.0],
        "kitten":    [0.85, 0.25, 0.15, 0.0],
        "airplane":  [0.0, 0.1, 0.05, 0.95],
        "orthogonal_example": [1.0, 0.0],  # deliberately 2D to show angle=90deg
    }

    print("=" * 70)
    print("Dot product and magnitude, computed by hand")
    print("=" * 70)
    cat, kitten = vectors["cat"], vectors["kitten"]
    print(f"cat     = {cat}")
    print(f"kitten  = {kitten}")
    print(f"dot(cat, kitten)      = {dot_product_by_hand(cat, kitten):.4f}")
    print(f"magnitude(cat)        = {magnitude_by_hand(cat):.4f}")
    print(f"magnitude(kitten)     = {magnitude_by_hand(kitten):.4f}")

    print("\n" + "=" * 70)
    print("Cosine similarity: hand-written vs. NumPy (should match exactly)")
    print("=" * 70)
    pairs = [("cat", "kitten"), ("cat", "airplane"), ("kitten", "airplane")]
    for name_a, name_b in pairs:
        a, b = vectors[name_a], vectors[name_b]
        by_hand = cosine_similarity_by_hand(a, b)
        by_numpy = cosine_similarity_numpy(np.array(a), np.array(b))
        match = "MATCH" if abs(by_hand - by_numpy) < 1e-9 else "MISMATCH"
        print(f"  {name_a:9s} vs {name_b:9s} -> by-hand={by_hand:.6f}  numpy={by_numpy:.6f}  [{match}]")

    print("\n" + "=" * 70)
    print("Orthogonal vectors: cosine similarity should be ~0")
    print("=" * 70)
    v1, v2 = [1.0, 0.0], [0.0, 1.0]
    sim = cosine_similarity_by_hand(v1, v2)
    print(f"  {v1} vs {v2} -> cosine similarity = {sim:.4f}  (perpendicular vectors -> 0)")

    print("\n" + "=" * 70)
    print("Interpretation")
    print("=" * 70)
    print(
        "'cat' and 'kitten' score close to 1.0: their vectors point in nearly\n"
        "the same direction. 'cat' and 'airplane' score close to 0: unrelated\n"
        "directions. This is exactly the computation a vector database runs --\n"
        "millions of times, over real embedding vectors with hundreds or\n"
        "thousands of dimensions instead of 4 -- when you search a RAG system\n"
        "(Track 3) for 'documents similar to this query.'"
    )


if __name__ == "__main__":
    main()
