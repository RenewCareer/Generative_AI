"""Lesson 3: why the same prompt gives different answers.

A model outputs a score for each possible next token. Temperature reshapes those scores
into probabilities before one token is sampled. No API key is needed: this is the real
arithmetic on toy numbers.

Run: python lessons/03_temperature_sampling.py
"""

import numpy as np

TOKENS = ["Paris", "beautiful", "a", "the", "banana"]
LOGITS = np.array([6.0, 3.5, 2.5, 2.0, -1.0])


def softmax_with_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    if temperature <= 0:
        probabilities = np.zeros_like(logits)
        probabilities[np.argmax(logits)] = 1.0
        return probabilities
    scaled = logits / temperature
    exponentials = np.exp(scaled - scaled.max())
    return exponentials / exponentials.sum()


def main() -> None:
    rng = np.random.default_rng(seed=7)
    print('Prompt: "The capital of France is ..."\n')
    for temperature in (0.0, 0.5, 1.0, 2.0):
        probabilities = softmax_with_temperature(LOGITS, temperature)
        print(f"temperature = {temperature}")
        for token, probability in zip(TOKENS, probabilities):
            print(f"  {token:<10}{probability:6.1%} {'#' * round(probability * 40)}")
        samples = rng.choice(TOKENS, size=8, p=probabilities)
        print(f"  8 samples : {' | '.join(samples)}\n")

    print("Takeaway: low temperature for extraction and classification, higher for brainstorming.")
    print("Even at temperature 0, providers do not promise identical output, so test with evals.")


if __name__ == "__main__":
    main()
