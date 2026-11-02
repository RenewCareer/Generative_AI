"""Lesson 2: release a prompt like code, by starting with a small share of real traffic.

Run: python lessons/02_prompt_canary.py
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.release import PromptRegistry, VariantStats, promotion_decision  # noqa: E402


def main() -> None:
    registry = PromptRegistry()
    print("Versions:")
    for version in registry.versions.values():
        print(f"  {version.version}: {version.description}")

    assignment = Counter(registry.select(f"user-{number}").version for number in range(10_000))
    print(f"\nConfig: {registry.canary_percent}% canary. Over 10,000 users: {dict(assignment)}")
    print(f"A user stays on one version: {registry.select('user-7').version} = {registry.select('user-7').version}\n")

    print("Promotion decisions:")
    baseline = VariantStats(requests=9000, errors=45, p95_ms=1800, quality=0.91)
    scenarios = {
        "Too little data yet": VariantStats(50, 0, 1700, 0.92),
        "Healthy canary": VariantStats(1000, 5, 1750, 0.92),
        "Answers got worse": VariantStats(1000, 5, 1700, 0.82),
        "Latency regression": VariantStats(1000, 5, 2600, 0.92),
    }
    for name, canary in scenarios.items():
        decision, reasons = promotion_decision(baseline, canary)
        print(f"  {name:<22}{decision.upper():<10}{reasons[0]}")

    registry.configure(active="1.0.0", canary=None)
    print(f"\nRollback is a config change. Active prompt: {registry.active}, canary traffic: {registry.canary_percent}%")


if __name__ == "__main__":
    main()
