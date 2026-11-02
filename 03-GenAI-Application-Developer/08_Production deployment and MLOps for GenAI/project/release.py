"""Prompt registry, canary routing, spend guard and promotion rules."""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from datetime import date
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class PromptVersion:
    version: str
    system: str
    description: str = ""


class PromptRegistry:
    """Prompts are files under version control, and config selects which one is live.

    Rolling back a bad prompt is then a config change, not an emergency code deployment.
    """

    def __init__(self, directory: Path = PROMPT_DIR) -> None:
        self.directory = directory
        self.versions = {
            data["version"]: PromptVersion(data["version"], data["system"], data.get("description", ""))
            for data in (json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("v*.json")))
        }
        config = json.loads((directory / "registry.json").read_text(encoding="utf-8"))
        self.configure(config["active"], config.get("canary"), config.get("canary_percent", 0))

    def configure(self, active: str, canary: str | None = None, canary_percent: int = 0) -> None:
        for version in filter(None, (active, canary)):
            if version not in self.versions:
                raise ValueError(f"Unknown prompt version: {version}")
        if not 0 <= canary_percent <= 100:
            raise ValueError("canary_percent must be between 0 and 100")
        self.active = active
        self.canary = canary
        self.canary_percent = canary_percent if canary else 0

    def select(self, user_id: str) -> PromptVersion:
        """Stable assignment: the same user always gets the same version."""
        bucket = int(hashlib.sha256(user_id.encode()).hexdigest(), 16) % 100
        if self.canary and bucket < self.canary_percent:
            return self.versions[self.canary]
        return self.versions[self.active]


class BudgetExceeded(RuntimeError):
    pass


class BudgetGuard:
    """A hard daily spend limit, so that a bug or an abuser cannot run up an unbounded bill."""

    def __init__(self, daily_limit_usd: float, input_per_m: float, output_per_m: float, today=date.today) -> None:
        self.daily_limit_usd = daily_limit_usd
        self.input_per_m = input_per_m
        self.output_per_m = output_per_m
        self.today = today
        self.spent_usd = 0.0
        self._day = today()
        self._lock = threading.Lock()

    def _roll(self) -> None:
        if self.today() != self._day:
            self._day = self.today()
            self.spent_usd = 0.0

    def check(self) -> None:
        with self._lock:
            self._roll()
            if self.spent_usd >= self.daily_limit_usd:
                raise BudgetExceeded("The daily AI budget has been used up.")

    def record(self, input_tokens: int, output_tokens: int) -> float:
        cost = input_tokens / 1e6 * self.input_per_m + output_tokens / 1e6 * self.output_per_m
        with self._lock:
            self._roll()
            self.spent_usd += cost
        return cost

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.daily_limit_usd - self.spent_usd)


@dataclass
class VariantStats:
    requests: int
    errors: int
    p95_ms: float
    quality: float  # From online evals or user feedback, between 0 and 1

    @property
    def error_rate(self) -> float:
        return self.errors / self.requests if self.requests else 0.0


def promotion_decision(
    baseline: VariantStats,
    canary: VariantStats,
    min_requests: int = 200,
    max_error_increase: float = 0.01,
    max_latency_ratio: float = 1.2,
    max_quality_drop: float = 0.02,
) -> tuple[str, list[str]]:
    """Compare canary with baseline, and return promote, wait or rollback with the reasons."""
    problems = []
    if canary.error_rate > baseline.error_rate + max_error_increase:
        problems.append(f"error rate {canary.error_rate:.1%} against {baseline.error_rate:.1%}")
    if canary.p95_ms > baseline.p95_ms * max_latency_ratio:
        problems.append(f"p95 latency {canary.p95_ms:.0f} ms against {baseline.p95_ms:.0f} ms")
    if canary.quality < baseline.quality - max_quality_drop:
        problems.append(f"quality {canary.quality:.2f} against {baseline.quality:.2f}")
    if problems:
        return "rollback", problems
    if canary.requests < min_requests:
        return "wait", [f"only {canary.requests} of {min_requests} requests so far"]
    return "promote", ["all signals are within limits"]
