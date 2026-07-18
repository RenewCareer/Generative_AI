"""
Intermediate example: softmax and temperature, implemented from scratch.

Requires: numpy (see requirements.txt).

An LLM's "next token" step produces one raw score (logit) per possible
token in its vocabulary. Softmax turns those raw scores into a valid
probability distribution. Temperature reshapes that distribution BEFORE
softmax is applied, controlling how "sharp" (deterministic) or "flat"
(random) the sampling is. This script makes both operations concrete on a
tiny 5-token toy vocabulary.

Run it with:
    python 02_intermediate_probability_softmax.py
"""

import numpy as np

# A toy vocabulary and made-up raw scores ("logits") a model might produce
# after seeing the prompt "The sky is". Higher score = model thinks this
# token is more likely to come next.
VOCAB = ["blue", "clear", "cloudy", "purple", "banana"]
LOGITS = np.array([4.2, 3.8, 3.1, 0.5, -2.0])


def softmax(logits: np.ndarray) -> np.ndarray:
    """Standard softmax, with the numerically-stable trick of subtracting
    the max logit first (prevents overflow in np.exp for large logits;
    does not change the resulting probabilities -- softmax is shift-invariant)."""
    shifted = logits - np.max(logits)
    exp_scores = np.exp(shifted)
    return exp_scores / exp_scores.sum()


def softmax_with_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    """Divide logits by temperature before softmax.
    - temperature < 1: sharpens the distribution (more deterministic)
    - temperature = 1: unchanged (standard softmax)
    - temperature > 1: flattens the distribution (more random)
    """
    return softmax(logits / temperature)


def print_distribution(vocab: list[str], probs: np.ndarray, label: str) -> None:
    print(f"\n{label}")
    for token, p in sorted(zip(vocab, probs), key=lambda x: -x[1]):
        bar = "#" * int(p * 50)
        print(f"  {token:8s} {p:6.1%}  {bar}")
    print(f"  (sum of probabilities = {probs.sum():.4f}, always 1.0 -- that's what makes it a valid distribution)")


def main() -> None:
    print("=" * 70)
    print(f"Raw logits for vocabulary {VOCAB}: {LOGITS}")
    print("=" * 70)
    print(
        "These raw numbers aren't probabilities yet -- they can be negative,\n"
        "and they don't sum to 1. Softmax fixes both problems."
    )

    base_probs = softmax(LOGITS)
    print_distribution(VOCAB, base_probs, "Standard softmax (temperature = 1.0):")

    print("\n" + "=" * 70)
    print("Now the same logits at three different temperatures")
    print("=" * 70)

    for temperature in [0.3, 1.0, 2.5]:
        probs = softmax_with_temperature(LOGITS, temperature)
        print_distribution(VOCAB, probs, f"Temperature = {temperature}:")

    print("\n" + "=" * 70)
    print("Interpretation")
    print("=" * 70)
    print(
        "At temperature=0.3, 'blue' dominates almost completely -- sampling\n"
        "from this distribution will pick 'blue' nearly every time. This is\n"
        "what a LOW temperature setting in a chat app does: safer, more\n"
        "repeatable output.\n\n"
        "At temperature=2.5, the distribution is much flatter -- even\n"
        "'banana' (a nonsensical continuation) gets a non-trivial chance of\n"
        "being sampled. This is what a HIGH temperature setting does: more\n"
        "variety, but more risk of an incoherent or off-topic output.\n\n"
        "Real LLMs run this exact computation over 50,000-200,000+ vocabulary\n"
        "tokens at every single generation step."
    )


if __name__ == "__main__":
    main()
