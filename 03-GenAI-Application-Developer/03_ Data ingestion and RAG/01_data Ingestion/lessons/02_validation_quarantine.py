"""Lesson 2: validate at the door, and quarantine rather than crash.

Run: python lessons/02_validation_quarantine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.ingest import validate_records  # noqa: E402

GOOD_TEXT = "Support requests should include the product name and any error code."
RECORDS = [
    {"doc_id": "guide", "source": "guide.txt", "source_type": "txt", "text": GOOD_TEXT},
    {"doc_id": "guide", "source": "copy.txt", "source_type": "txt", "text": GOOD_TEXT},
    {"doc_id": "empty", "source": "empty.txt", "source_type": "txt", "text": "   "},
    {"doc_id": "", "source": "noid.txt", "source_type": "txt", "text": GOOD_TEXT},
    {"doc_id": "nosource", "source_type": "txt", "text": GOOD_TEXT},
]


def main() -> None:
    report = validate_records(RECORDS)
    print(f"Accepted {len(report.valid)} of {len(RECORDS)} records\n")
    for document in report.valid:
        print(f"  OK   {document.doc_id}  sha256={document.content_hash[:12]}...")
    print()
    for item in report.quarantined:
        print(f"  HELD {item['record'].get('source', '?'):<12} {item['reason']}")
    print("\nA quiet data bug here becomes a wrong answer later. Quarantine makes it visible.")
    print("In production, alert when the quarantine rate jumps: the source format may have changed.")


if __name__ == "__main__":
    main()
