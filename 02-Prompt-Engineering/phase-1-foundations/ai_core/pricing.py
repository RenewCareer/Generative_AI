"""Token pricing and cost estimation.

Prices CHANGE. These are list prices in USD per 1M tokens and must be checked
against https://openai.com/api/pricing before you rely on them. Your billing
dashboard (https://platform.openai.com/usage) is the source of truth.
"""
from __future__ import annotations

# model prefix -> (input, cached_input, output) USD per 1M tokens
PRICES: dict[str, tuple[float, float, float]] = {
    "gpt-5": (1.25, 0.125, 10.00),
    "gpt-5-mini": (0.25, 0.025, 2.00),
    "gpt-5-nano": (0.05, 0.005, 0.40),
    "gpt-4.1": (2.00, 0.50, 8.00),
    "gpt-4.1-mini": (0.40, 0.10, 1.60),
    "gpt-4.1-nano": (0.10, 0.025, 0.40),
    "gpt-4o": (2.50, 1.25, 10.00),
    "gpt-4o-mini": (0.15, 0.075, 0.60),
}


def _lookup(model: str) -> tuple[float, float, float] | None:
    # The API often returns a dated snapshot ("gpt-5-mini-2025-08-07"), so match
    # the longest known prefix. Longest wins so "gpt-5-mini" beats "gpt-5".
    matches = [k for k in PRICES if model == k or model.startswith(k + "-")]
    return PRICES[max(matches, key=len)] if matches else None


def estimate_cost(
    model: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0
) -> float | None:
    """Return estimated USD cost, or None if the model isn't in the table."""
    price = _lookup(model)
    if price is None:
        return None
    p_in, p_cached, p_out = price
    uncached = input_tokens - cached_tokens
    return (uncached * p_in + cached_tokens * p_cached + output_tokens * p_out) / 1_000_000
