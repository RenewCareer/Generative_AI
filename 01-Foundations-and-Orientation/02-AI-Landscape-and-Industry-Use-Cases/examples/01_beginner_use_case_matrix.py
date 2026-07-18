"""
Beginner example: load and query a small "GenAI use case by industry" dataset.

Requires: pandas (see requirements.txt).

This script teaches the load-filter-aggregate pattern you'll reuse constantly:
read structured data into a DataFrame, filter rows by condition, and
summarize with group-by counts.

Run it with:
    python 01_beginner_use_case_matrix.py
"""

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "industry_use_cases.csv"


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    print("=" * 70)
    print(f"Loaded {len(df)} GenAI use cases across {df['industry'].nunique()} industries")
    print("=" * 70)
    print(df.head(5).to_string(index=False))

    print("\n" + "=" * 70)
    print("Query 1: all use cases for the Healthcare industry")
    print("=" * 70)
    healthcare = df[df["industry"] == "Healthcare"]
    print(healthcare[["use_case", "genai_capability", "modality"]].to_string(index=False))

    print("\n" + "=" * 70)
    print("Query 2: all TEXT-modality use cases that are still 'Emerging'")
    print("=" * 70)
    emerging_text = df[(df["modality"] == "text") & (df["maturity"] == "Emerging")]
    print(emerging_text[["industry", "use_case"]].to_string(index=False))

    print("\n" + "=" * 70)
    print("Query 3: how many use cases per modality?")
    print("=" * 70)
    print(df["modality"].value_counts().to_string())

    print("\n" + "=" * 70)
    print("Query 4: which industry has the most documented use cases?")
    print("=" * 70)
    counts = df.groupby("industry").size().sort_values(ascending=False)
    print(counts.to_string())
    print(f"\nTop industry: {counts.idxmax()} ({counts.max()} use cases)")


if __name__ == "__main__":
    main()
