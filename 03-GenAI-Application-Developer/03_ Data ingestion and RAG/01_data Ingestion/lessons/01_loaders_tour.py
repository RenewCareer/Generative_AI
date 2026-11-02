"""Lesson 1: many formats in, one document shape out.

Run: python lessons/01_loaders_tour.py
"""

import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from genai_kit import COURSE_DATA  # noqa: E402
from project.ingest import load_csv, load_json, load_pdf, load_text  # noqa: E402

PDF = UNIT.parent / "02_Document_processing_chunking" / "data" / "raw" / "pdf" / "NIST.AI.100-1.pdf"


def show(label: str, records: list[dict]) -> None:
    first = records[0]
    preview = " ".join(first["text"].split())[:70]
    print(f"{label:<6}{len(records):>4} docs | id={first['doc_id']:<28} | {preview}...")


def main() -> None:
    show("TXT", load_text(UNIT / "quick_guide.txt"))
    show("MD", load_text(COURSE_DATA / "docs" / "refund_policy.md"))
    show("CSV", load_csv(COURSE_DATA / "reviews.csv"))
    show("JSON", load_json(COURSE_DATA / "orders.json"))
    if PDF.exists():
        show("PDF", load_pdf(PDF))
    print("\nEvery loader returns the same keys:", sorted(load_csv(COURSE_DATA / "reviews.csv")[0]))
    print("Everything downstream only needs to understand that one shape.")


if __name__ == "__main__":
    main()
