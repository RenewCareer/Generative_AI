"""Reliability patterns: circuit breaker and fallback chain."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

from genai_kit import LLMClient, LLMResponse

logger = logging.getLogger("resilience")


class CircuitOpenError(RuntimeError):
    """Raised without calling the provider while the circuit is open."""


class CircuitBreaker:
    """After repeated failures, stop calling a broken service, and try again later.

    CLOSED: normal. OPEN: fail fast. HALF_OPEN: let one trial request through.
    Failing fast protects users from long timeouts, and gives the provider room to recover.
    """

    def __init__(self, failure_threshold: int = 3, recovery_s: float = 30.0, clock: Callable[[], float] = time.monotonic):
        self.failure_threshold = failure_threshold
        self.recovery_s = recovery_s
        self.clock = clock
        self.failures = 0
        self.opened_at: float | None = None

    @property
    def state(self) -> str:
        if self.opened_at is None:
            return "CLOSED"
        return "HALF_OPEN" if self.clock() - self.opened_at >= self.recovery_s else "OPEN"

    def call(self, function: Callable[[], Any]) -> Any:
        if self.state == "OPEN":
            raise CircuitOpenError("Circuit is open.")
        try:
            result = function()
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold or self.opened_at is not None:
                self.opened_at = self.clock()
            raise
        self.failures = 0
        self.opened_at = None
        return result


class FallbackLLM:
    """Try each provider in order, each guarded by its own circuit breaker."""

    def __init__(self, clients: list[LLMClient], breaker_factory: Callable[[], CircuitBreaker] = CircuitBreaker):
        if not clients:
            raise ValueError("At least one client is required.")
        self.clients = clients
        self.breakers = [breaker_factory() for _ in clients]
        self.provider = "fallback"
        self.model = clients[0].model

    def complete(self, messages, **kwargs) -> LLMResponse:
        last_error: Exception | None = None
        for client, breaker in zip(self.clients, self.breakers):
            try:
                return breaker.call(lambda: client.complete(messages, **kwargs))
            except Exception as error:
                logger.warning("%s/%s failed: %s", client.provider, client.model, type(error).__name__)
                last_error = error
        raise RuntimeError("All providers failed.") from last_error
