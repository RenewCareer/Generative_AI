"""Lesson 2: red-team your own guardrails, and look hard at what gets through.

Run: python lessons/02_red_team.py
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.evaluate import load_redteam  # noqa: E402
from project.guards import check_input  # noqa: E402


def main() -> None:
    attacks = load_redteam()
    outcomes = Counter()
    totals = Counter()
    missed = []
    for attack in attacks:
        verdict = check_input(attack["prompt"])
        totals[attack["category"]] += 1
        if verdict.allowed:
            missed.append(attack)
        else:
            outcomes[attack["category"]] += 1

    print(f"{'category':<20}{'blocked':>10}")
    for category, total in totals.items():
        print(f"{category:<20}{outcomes[category]:>6} / {total}")

    print(f"\nGOT THROUGH ({len(missed)}):")
    for attack in missed:
        print(f"  {attack['id']} [{attack['category']}] {attack['prompt']}")

    print("\nPattern filters catch known phrasings, and paraphrased attacks get past them. That is why")
    print("a filter is only one layer. The model's training, the canary, output checks and, above all,")
    print("limited permissions must hold when this layer fails. It will fail.")


if __name__ == "__main__":
    main()
