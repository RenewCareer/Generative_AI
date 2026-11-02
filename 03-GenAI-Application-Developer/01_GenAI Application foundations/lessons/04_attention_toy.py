"""Lesson 4: the core idea of a transformer in 25 lines of NumPy.

Self-attention lets each word look at the other words and decide which matter. In
"the bank of the river", attention pulls "bank" towards the meaning set by "river".
The vectors are hand-picked to make the point. A real model learns them.

Run: python lessons/04_attention_toy.py
"""

import numpy as np

WORDS = ["the", "bank", "of", "river"]
# Hand-made 3D vectors: [finance-ness, water-ness, grammar-ness]
EMBEDDINGS = np.array(
    [
        [0.0, 0.0, 1.0],
        [0.7, 0.7, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
    ]
)


def self_attention(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Scaled dot-product attention: softmax(Q @ K.T / sqrt(d)) @ V, with Q = K = V = x."""
    scores = x @ x.T / np.sqrt(x.shape[1])
    weights = np.exp(scores) / np.exp(scores).sum(axis=1, keepdims=True)
    return weights, weights @ x


def main() -> None:
    weights, contextual = self_attention(EMBEDDINGS)

    print("Attention weights: how much each row word looks at each column word")
    print(" " * 8 + "".join(f"{word:>8}" for word in WORDS))
    for word, row in zip(WORDS, weights):
        print(f"{word:<8}" + "".join(f"{value:8.2f}" for value in row))

    before, after = EMBEDDINGS[1], contextual[1]
    print("\n'bank' vector  [finance, water, grammar]")
    print(f"  before attention: {np.round(before, 2)}")
    print(f"  after attention : {np.round(after, 2)}")
    print(f"\nWater minus finance moved from {before[1] - before[0]:.2f} to {after[1] - after[0]:.2f}.")
    print("The word 'river' pulled 'bank' towards its water meaning. That is attention.")


if __name__ == "__main__":
    main()
