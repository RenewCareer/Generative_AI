"""Lesson 3: retrieval metrics worked by hand on one small example.

Run: python lessons/03_retrieval_metrics.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.metrics import hit_at_k, ndcg_at_k, reciprocal_rank  # noqa: E402

RELEVANT = "refund_policy"
SYSTEMS = {
    "System A (rank 1)": ["refund_policy", "warranty", "shipping_policy"],
    "System B (rank 3)": ["warranty", "shipping_policy", "refund_policy"],
    "System C (missed)": ["warranty", "shipping_policy", "leave_policy"],
}


def main() -> None:
    print(f"The relevant document is {RELEVANT}\n")
    print(f"{'':<20}{'hit@3':>8}{'hit@1':>8}{'MRR':>8}{'nDCG@3':>9}")
    for name, retrieved in SYSTEMS.items():
        print(
            f"{name:<20}{hit_at_k(retrieved, RELEVANT, 3):>8.2f}{hit_at_k(retrieved, RELEVANT, 1):>8.2f}"
            f"{reciprocal_rank(retrieved, RELEVANT):>8.2f}{ndcg_at_k(retrieved, RELEVANT, 3):>9.2f}"
        )
    print("\nhit@k: was it found at all? MRR and nDCG: was it found early?")
    print("Rank matters because the model pays most attention to what comes first, and because")
    print("smaller k means fewer tokens and lower cost.")


if __name__ == "__main__":
    main()
