"""Lesson 2: cleaning, shown before and after.

Run: python lessons/02_cleaning_before_after.py
"""

import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from cleaners import clean_text, remove_repeated_lines  # noqa: E402
from src.extractors.pdf_extractor import extract_pdf  # noqa: E402

DIRTY = "The ﬁrst   rule of risk manage-\nment: measure​ it.\n\n\n\n\nThen act."


def main():
    print("BEFORE:", repr(DIRTY))
    print("AFTER :", repr(clean_text(DIRTY)))

    print("\nHeaders and footers repeat on every page. They add noise to every chunk:")
    bodies = ["Measure the risk first.", "Assign an owner.", "Review it every quarter."]
    pages = [f"ACME CONFIDENTIAL\n{body}\nPage {n} of 3" for n, body in enumerate(bodies, start=1)]
    print("  before:", repr(pages[0]))
    print("  after :", repr(remove_repeated_lines(pages)[0]))

    pdf = UNIT / "data" / "raw" / "pdf" / "NIST.AI.100-1.pdf"
    if pdf.exists():
        raw = [page["content"] for page in extract_pdf(str(pdf))]
        cleaned = [clean_text(page) for page in remove_repeated_lines(raw)]
        before, after = sum(map(len, raw)), sum(map(len, cleaned))
        print(f"\nOn the real NIST PDF: {before:,} characters reduced to {after:,} ({1 - after / before:.0%} removed)")


if __name__ == "__main__":
    main()
