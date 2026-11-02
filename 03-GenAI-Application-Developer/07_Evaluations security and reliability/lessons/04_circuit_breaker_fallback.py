"""Lesson 4: when a provider goes down, fail fast and fall back.

Run: python lessons/04_circuit_breaker_fallback.py
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient  # noqa: E402
from project.resilience import CircuitBreaker, FallbackLLM  # noqa: E402

MESSAGE = [{"role": "user", "content": "Hello"}]


class Provider(MockClient):
    def __init__(self, name: str, healthy: bool = True) -> None:
        super().__init__(lambda messages, system, tools: f"reply from {name}")
        self.name = name
        self.healthy = healthy
        self.calls = 0

    def complete(self, *args, **kwargs):
        self.calls += 1
        if not self.healthy:
            raise TimeoutError(f"{self.name} timed out")
        return super().complete(*args, **kwargs)


def main() -> None:
    logging.disable(logging.WARNING)  # Keep the classroom output readable.
    now = [0.0]
    primary = Provider("primary", healthy=False)
    backup = Provider("backup")
    llm = FallbackLLM([primary, backup], lambda: CircuitBreaker(failure_threshold=3, recovery_s=30, clock=lambda: now[0]))

    print(f"{'request':<10}{'answer':<20}{'breaker':<12}{'primary calls':>14}")
    for number in range(1, 7):
        reply = llm.complete(MESSAGE).text
        print(f"{number:<10}{reply:<20}{llm.breakers[0].state:<12}{primary.calls:>14}")
    print("After 3 failures, requests stop waiting on the broken provider.\n")

    now[0] += 31
    primary.healthy = True
    reply = llm.complete(MESSAGE).text
    print(f"31 seconds later: one trial request succeeds: {reply}, breaker {llm.breakers[0].state}")


if __name__ == "__main__":
    main()
