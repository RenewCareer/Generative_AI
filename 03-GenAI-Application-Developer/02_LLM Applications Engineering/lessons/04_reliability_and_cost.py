"""Lesson 4: retries with backoff, and a cost ledger.

Both provider SDKs already retry connection errors, 429s and 5xx responses. Set
max_retries and timeout on the client. This lesson shows what they do, because you need
the same pattern around your own multi-step workflows.

Run: python lessons/04_reliability_and_cost.py
"""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from genai_kit import Usage

T = TypeVar("T")


class RetryableError(Exception):
    """Temporary: rate limit, timeout, 5xx."""


class PermanentError(Exception):
    """Will not improve on retry: bad request, bad key, content refused."""


def backoff_delay(attempt: int, base: float = 0.5, cap: float = 20.0, rng: random.Random | None = None) -> float:
    """Exponential backoff with full jitter, so clients do not all retry at the same moment."""
    return (rng or random).uniform(0, min(cap, base * 2**attempt))


def call_with_retries(
    call: Callable[[], T],
    max_attempts: int = 4,
    sleep: Callable[[float], None] = lambda seconds: None,
    rng: random.Random | None = None,
) -> T:
    for attempt in range(max_attempts):
        try:
            return call()
        except RetryableError as error:
            if attempt == max_attempts - 1:
                raise
            delay = backoff_delay(attempt, rng=rng)
            print(f"  attempt {attempt + 1} failed ({error}), waiting {delay:.2f}s")
            sleep(delay)
    raise AssertionError("unreachable")


@dataclass
class CostLedger:
    """Prices per million tokens. Read them from configuration, because they change."""

    input_per_m: float
    output_per_m: float
    input_tokens: int = 0
    output_tokens: int = 0
    budget_usd: float = float("inf")

    def record(self, usage: Usage) -> None:
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        if self.spent_usd > self.budget_usd:
            raise RuntimeError(f"Budget exceeded: ${self.spent_usd:.4f} > ${self.budget_usd:.4f}")

    @property
    def spent_usd(self) -> float:
        return self.input_tokens / 1e6 * self.input_per_m + self.output_tokens / 1e6 * self.output_per_m


def main() -> None:
    print("A flaky service that fails twice, then succeeds:")
    failures = iter([RetryableError("429 rate limited"), RetryableError("503 overloaded")])

    def flaky() -> str:
        for error in failures:
            raise error
        return "success"

    print(f"  result: {call_with_retries(flaky, rng=random.Random(1))}\n")

    print("A permanent error is not retried, so it does not waste time or money:")
    calls = 0

    def bad_request() -> str:
        nonlocal calls
        calls += 1
        raise PermanentError("400 invalid request")

    try:
        call_with_retries(bad_request)
    except PermanentError as error:
        print(f"  gave up after {calls} call: {error}\n")

    print("A cost ledger stops a runaway job (illustrative prices):")
    ledger = CostLedger(input_per_m=0.40, output_per_m=1.60, budget_usd=0.002)
    try:
        for number in range(1, 100):
            ledger.record(Usage(1000, 300))
            print(f"  call {number}: ${ledger.spent_usd:.5f}")
    except RuntimeError as error:
        print(f"  stopped: {error}")


if __name__ == "__main__":
    main()
