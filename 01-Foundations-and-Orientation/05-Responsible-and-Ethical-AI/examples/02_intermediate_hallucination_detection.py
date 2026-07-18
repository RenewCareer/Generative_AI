"""
Intermediate example: detect hallucinated facts by extracting claimed
values and checking them against a trusted knowledge base.

No third-party dependencies -- pure Python standard library (`re`).

The claims below simulate "what an LLM said" -- some are accurate, one is
deliberately wrong, to mimic a hallucination. Real hallucination detection
in production systems works on the same core idea: extract the specific,
checkable factual assertion from a longer generated passage, then verify
it against a trusted source. Track 3's RAG systems automate the "trusted
source" half of this by retrieving relevant real documents before the
model even generates its answer, which reduces (but doesn't eliminate)
this failure mode.

Run it with:
    python 02_intermediate_hallucination_detection.py
"""

import re

# Our "trusted source" -- in a real system this might be a verified
# database, a retrieved document set (Track 3), or a curated fact sheet.
# Values are stored as plain numbers (as strings) for easy comparison.
KNOWLEDGE_BASE = {
    "eiffel_tower_completion_year": "1889",
    "python_first_release_year": "1991",
    "mount_everest_height_m": "8849",
    "great_wall_total_length_km": "21196",  # per the 2012 official Chinese survey (all dynasties, all branches)
}

# Each claim simulates one sentence an LLM might generate. `fact_key` tells
# our checker which knowledge-base entry to verify against -- in a real
# system, an earlier NLP/extraction step (or the LLM itself, asked to cite
# structured claims) would produce this mapping automatically.
CLAIMS = [
    {
        "fact_key": "eiffel_tower_completion_year",
        "text": "The Eiffel Tower was completed in 1889 and remains a global icon.",
    },
    {
        "fact_key": "python_first_release_year",
        "text": "The Python programming language was first released in 1991 by Guido van Rossum.",
    },
    {
        "fact_key": "mount_everest_height_m",
        "text": "Mount Everest stands at approximately 8849 meters above sea level.",
    },
    {
        # Deliberately wrong -- simulates a hallucinated statistic that
        # SOUNDS plausible and is stated with total confidence.
        "fact_key": "great_wall_total_length_km",
        "text": "The Great Wall of China stretches approximately 8850 kilometers in total.",
    },
]


def extract_number(text: str) -> str | None:
    """Pull the first number out of a sentence, stripping thousands
    separators, so it can be compared against the knowledge base."""
    match = re.search(r"\d[\d,]*", text)
    if not match:
        return None
    return match.group(0).replace(",", "")


def verify_claim(claim: dict) -> dict:
    """Check one claim's extracted value against the knowledge base.
    Returns a report dict with a verdict of 'confirmed', 'hallucinated',
    or 'unverifiable' (no ground truth available for this fact_key)."""
    fact_key = claim["fact_key"]
    claimed_value = extract_number(claim["text"])
    true_value = KNOWLEDGE_BASE.get(fact_key)

    if true_value is None:
        verdict = "unverifiable"
    elif claimed_value == true_value:
        verdict = "confirmed"
    else:
        verdict = "hallucinated"

    return {
        "text": claim["text"],
        "fact_key": fact_key,
        "claimed_value": claimed_value,
        "true_value": true_value,
        "verdict": verdict,
    }


def main() -> None:
    print("=" * 70)
    print("Hallucination detection: extract-then-verify")
    print("=" * 70)

    reports = [verify_claim(claim) for claim in CLAIMS]

    for report in reports:
        icon = {"confirmed": "[OK]", "hallucinated": "[FLAGGED]", "unverifiable": "[UNVERIFIABLE]"}[report["verdict"]]
        print(f"\n{icon} {report['text']!r}")
        print(f"    claimed value: {report['claimed_value']}   trusted value: {report['true_value']}")

    confirmed = sum(1 for r in reports if r["verdict"] == "confirmed")
    hallucinated = sum(1 for r in reports if r["verdict"] == "hallucinated")

    print("\n" + "=" * 70)
    print(f"Summary: {confirmed} confirmed, {hallucinated} flagged as potential hallucination")
    print("=" * 70)
    print(
        "The flagged claim about the Great Wall's length was stated with\n"
        "exactly the same fluent, confident tone as the correct claims --\n"
        "there was NOTHING in the surface-level writing quality that gave\n"
        "away the error. This is the core danger of hallucination: fluency\n"
        "is not a signal of correctness, and confident-sounding text can be\n"
        "just as wrong as hedging text. The only reliable fix is checking\n"
        "claims against a trusted, verifiable source, which is exactly what\n"
        "Retrieval Augmented Generation (Track 3) is designed to enable."
    )


if __name__ == "__main__":
    main()
