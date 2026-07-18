"""
Intermediate example: a simple rules-based GenAI use-case recommender.

Requires: pandas (see requirements.txt).

Given an industry and a free-text problem description, this recommends
the closest-matching documented use case by keyword overlap. It is
deliberately simple (no ML, no embeddings) -- the point is to practice the
"structured data + query logic = decision support" pattern before you
rebuild this same idea with an LLM in Track 3 (semantic search / RAG will
replace the crude keyword matching used here).

Run it with:
    python 02_intermediate_use_case_recommender.py
"""

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "industry_use_cases.csv"


def recommend(df: pd.DataFrame, industry: str, problem_description: str) -> pd.DataFrame:
    """Return use cases for `industry`, ranked by keyword overlap with
    `problem_description`, most relevant first."""
    candidates = df[df["industry"].str.lower() == industry.lower()].copy()
    if candidates.empty:
        return candidates

    problem_words = set(problem_description.lower().split())

    def score(row: pd.Series) -> int:
        use_case_words = set(row["use_case"].lower().split())
        capability_words = set(row["genai_capability"].lower().split())
        return len(problem_words & (use_case_words | capability_words))

    candidates["match_score"] = candidates.apply(score, axis=1)
    # Prefer established use cases when scores tie -- a safer real-world bet.
    candidates["maturity_rank"] = (candidates["maturity"] == "Established").astype(int)
    return candidates.sort_values(
        by=["match_score", "maturity_rank"], ascending=[False, False]
    )


def print_recommendation(df: pd.DataFrame, industry: str, problem: str) -> None:
    print(f"\nIndustry: {industry}")
    print(f"Problem:  {problem!r}")
    results = recommend(df, industry, problem)
    if results.empty:
        print("  No use cases documented for this industry.")
        return
    top = results.iloc[0]
    print(f"  -> Best match: {top['use_case']} ({top['genai_capability']}, "
          f"{top['modality']}, {top['maturity']}, score={top['match_score']})")
    if len(results) > 1:
        print("  Other candidates:")
        for _, row in results.iloc[1:3].iterrows():
            print(f"     - {row['use_case']} (score={row['match_score']})")


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    print("=" * 70)
    print("GenAI Use-Case Recommender (keyword-matching prototype)")
    print("=" * 70)

    scenarios = [
        ("Legal", "we need help drafting contracts faster"),
        ("Retail", "our customers want a chatbot for support conversation"),
        ("Software", "we want to automatically review code for bugs"),
        ("Marketing", "we need to generate ad copy at scale"),
    ]

    for industry, problem in scenarios:
        print_recommendation(df, industry, problem)

    print("\n" + "=" * 70)
    print("Note on this approach's limits:")
    print("=" * 70)
    print(
        "This recommender only matches LITERAL overlapping words. It would\n"
        "fail on a synonym like 'assemble contracts' instead of 'draft\n"
        "contracts' -- it has no notion of MEANING, only string overlap.\n"
        "This exact limitation is why Track 3 introduces embeddings and\n"
        "vector search: representing meaning as vectors lets you match on\n"
        "semantic similarity instead of exact keyword overlap."
    )


if __name__ == "__main__":
    main()
