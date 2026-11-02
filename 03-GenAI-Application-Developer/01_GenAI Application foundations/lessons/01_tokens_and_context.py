"""Lesson 1: tokens, context windows and cost, the three budgets of every LLM call.

Run: python lessons/01_tokens_and_context.py
"""

import re
from dataclasses import dataclass


def estimate_tokens(text: str) -> int:
    """Rule of thumb for English: about 4 characters per token.

    Good for planning. For exact counts use the provider's tokenizer or token-counting
    endpoint, because each model family tokenizes differently.
    """
    return max(1, round(len(text) / 4))


def rough_token_pieces(text: str) -> list[str]:
    """Split text the way tokenizers tend to: words, punctuation, and word fragments."""
    pieces: list[str] = []
    for word in re.findall(r"\s*\w+|[^\w\s]", text):
        pieces.extend(word[i : i + 6] for i in range(0, len(word), 6))
    return pieces


@dataclass
class ContextBudget:
    """How one request spends the model's context window."""

    window: int
    system: int
    history: int
    retrieved: int
    reserved_for_output: int

    @property
    def used(self) -> int:
        return self.system + self.history + self.retrieved + self.reserved_for_output

    @property
    def remaining(self) -> int:
        return self.window - self.used


def request_cost(input_tokens: int, output_tokens: int, input_per_m: float, output_per_m: float) -> float:
    """Cost in dollars. Prices are quoted per million tokens, and output usually costs more."""
    return input_tokens / 1_000_000 * input_per_m + output_tokens / 1_000_000 * output_per_m


def main() -> None:
    sentence = "Tokenization splits text into pieces that models can process."
    pieces = rough_token_pieces(sentence)
    print("1) TEXT BECOMES TOKENS")
    print(f"   Text    : {sentence}")
    print(f"   Pieces  : {pieces}")
    print(f"   Estimate: {estimate_tokens(sentence)} tokens from {len(sentence)} characters\n")

    budget = ContextBudget(window=128_000, system=400, history=6_000, retrieved=8_000, reserved_for_output=2_000)
    print("2) THE CONTEXT WINDOW IS SHARED")
    for name in ("system", "history", "retrieved", "reserved_for_output"):
        tokens = getattr(budget, name)
        print(f"   {name:<20}{tokens:>8,} {'#' * max(1, tokens // 500)}")
    print(f"   {'remaining':<20}{budget.remaining:>8,}\n")

    # Example prices only. Always check the provider's current pricing page.
    input_price, output_price = 0.40, 1.60
    one_call = request_cost(14_400, 500, input_price, output_price)
    print("3) COST COMPOUNDS AT SCALE")
    print(f"   Example price: ${input_price}/M input, ${output_price}/M output (illustrative)")
    print(f"   One call        : ${one_call:.5f}")
    print(f"   10,000 calls/day: ${one_call * 10_000:,.2f} per day")
    print(f"   Over 30 days    : ${one_call * 10_000 * 30:,.2f} per month")


if __name__ == "__main__":
    main()
