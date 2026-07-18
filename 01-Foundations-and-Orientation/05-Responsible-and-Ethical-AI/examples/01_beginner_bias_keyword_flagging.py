"""
Beginner example: flag potentially biased or exclusionary language in text.

No third-party dependencies -- pure Python standard library.

This is a simplified version of a real technique used in responsible-AI
tooling: scanning AI-assisted or AI-generated content for language
patterns known to discourage certain groups of readers/applicants, before
that content ships. Real tools use much larger, better-researched term
lists and often ML classifiers -- this keyword version is for building
intuition about WHAT the technique is checking for and WHY.

Run it with:
    python 01_beginner_bias_keyword_flagging.py
"""

# Each category maps a flagged term to a brief note on why it's flagged
# and a more neutral alternative. This list is illustrative, not exhaustive --
# real-world bias-linting tools maintain much larger, evolving term lists.
FLAGGED_TERMS = {
    # Gender-coded language
    "ninja": ("gender-coded (masculine-coded)", "skilled / expert"),
    "rockstar": ("gender-coded (masculine-coded)", "high performer"),
    "he will": ("gendered pronoun assumption", "they will"),
    "guys": ("gendered group term", "everyone / team"),
    # Age-coded language
    "young and energetic": ("age discrimination risk", "motivated"),
    "digital native": ("age discrimination risk", "comfortable with technology"),
    "recent graduate": ("age discrimination risk", "early-career candidate"),
    # Ableist language
    "must be able to stand for long periods": ("ableist -- excludes without justification", "role requires prolonged standing; accommodations available"),
    "crazy fast": ("ableist / mental-health-stigmatizing", "very fast"),
    # Exclusionary culture-fit language
    "culture fit": ("vague, can mask bias", "culture ADD (what new perspective they bring)"),
    "work hard play hard": ("can signal poor work-life balance expectations", "collaborative, results-driven team"),
}

SAMPLE_JOB_POSTINGS = [
    (
        "Senior Engineer",
        "We're looking for a coding ninja who is a real rockstar developer. "
        "He will own our backend systems and thrive in a work hard play hard culture.",
    ),
    (
        "Marketing Associate",
        "Ideal candidate is a young and energetic digital native who is a "
        "great culture fit for our growing team.",
    ),
    (
        "Warehouse Associate",
        "Candidates must be able to stand for long periods and lift up to 50 lbs. "
        "We move crazy fast here, so hit the ground running.",
    ),
    (
        "Data Analyst",
        "We're seeking a detail-oriented analyst with strong SQL skills to join "
        "our collaborative team. Recent graduates are encouraged to apply.",
    ),
]


def scan_for_bias(text: str) -> list[tuple[str, str, str]]:
    """Return a list of (flagged_term, reason, suggested_alternative) for
    every flagged term found in `text` (case-insensitive)."""
    text_lower = text.lower()
    findings = []
    for term, (reason, alternative) in FLAGGED_TERMS.items():
        if term in text_lower:
            findings.append((term, reason, alternative))
    return findings


def main() -> None:
    print("=" * 70)
    print("Bias / exclusionary language scan of sample job postings")
    print("=" * 70)

    total_findings = 0
    for title, posting_text in SAMPLE_JOB_POSTINGS:
        print(f"\nPosting: {title}")
        print(f"  Text: {posting_text!r}")

        findings = scan_for_bias(posting_text)
        if not findings:
            print("  No flagged terms found.")
            continue

        total_findings += len(findings)
        print(f"  Found {len(findings)} flagged term(s):")
        for term, reason, alternative in findings:
            print(f"    - {term!r}  [{reason}]  -> consider: {alternative!r}")

    print("\n" + "=" * 70)
    print(f"Total flagged terms across all postings: {total_findings}")
    print("=" * 70)
    print(
        "Notice: none of these terms are automatically discriminatory in\n"
        "isolation -- this is a HEURISTIC screen meant to prompt human review,\n"
        "not an automatic rejection. That distinction (flag-for-review vs.\n"
        "auto-reject) matters enormously in responsible AI system design,\n"
        "and you'll see it again in Track 4's governance material."
    )


if __name__ == "__main__":
    main()
