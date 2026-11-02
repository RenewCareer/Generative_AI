"""Lesson 1: embeddings turn text into coordinates, and closeness stands in for relevance.

Part 1 is hand-made 2D vectors, so the geometry is visible. Part 2 uses whichever embedder
is configured. With no API key it uses word overlap, and shows what that misses.

Run: python lessons/01_embedding_intuition.py
"""

import numpy as np

from genai_kit import get_embedder

# Hand-made coordinates: [is_about_animals, is_about_vehicles]
TOY = {
    "dog": np.array([0.95, 0.05]),
    "puppy": np.array([0.90, 0.10]),
    "car": np.array([0.05, 0.95]),
    "truck": np.array([0.10, 0.90]),
}


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """1 means the same direction, 0 means unrelated, -1 means opposite."""
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    print("PART 1: toy vectors, the geometry")
    for word in ("puppy", "car", "truck"):
        print(f"  cosine(dog, {word:<6}) = {cosine(TOY['dog'], TOY[word]):.3f}")

    embedder = get_embedder()
    query = "How do I get my money back?"
    sentences = [
        "Customers may return most items within 30 days for a full refund.",
        "Money orders are not accepted at the back office.",
        "The Terra band is water resistant to 50 metres.",
    ]
    vectors = embedder.embed([query, *sentences])

    print(f"\nPART 2: real text, using embedder '{embedder.name}'")
    print(f"  Each text becomes {vectors.shape[1]} numbers.")
    print(f"  Query: {query}")
    for sentence, vector in sorted(zip(sentences, vectors[1:]), key=lambda pair: -float(vectors[0] @ pair[1])):
        print(f"  {float(vectors[0] @ vector):+.3f}  {sentence}")

    if embedder.name == "hashing-offline":
        print("\nNotice the failure: the refund sentence answers the question but shares no words")
        print("with it, while the money-order sentence shares 'money' and 'back'. Word overlap")
        print("cannot see meaning. Add an OpenAI key and rerun: the refund sentence should move")
        print("up, because a real embedding model places 'money back' near 'refund'.")


if __name__ == "__main__":
    main()
