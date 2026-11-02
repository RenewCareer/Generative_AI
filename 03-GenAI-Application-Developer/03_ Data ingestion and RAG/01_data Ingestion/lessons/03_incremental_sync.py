"""Lesson 3: idempotent, incremental ingestion with content hashes.

Re-embedding everything nightly is slow and expensive. Hashes tell us what changed.

Run: python lessons/03_incremental_sync.py
"""

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import COURSE_DATA  # noqa: E402
from project.ingest import run  # noqa: E402


def report(label, result) -> None:
    print(
        f"{label:<26} added={len(result.added)} updated={len(result.updated)} "
        f"unchanged={len(result.unchanged)} deleted={len(result.deleted)}"
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source, state = Path(temp, "source"), Path(temp, "state")
        shutil.copytree(COURSE_DATA / "docs", source)

        report("1. First run", run(source, state))
        report("2. Run again, no changes", run(source, state))

        target = source / "refund_policy.md"
        target.write_text(target.read_text(encoding="utf-8").replace("30 days", "45 days"), encoding="utf-8")
        result = run(source, state)
        report("3. Edited one document", result)
        print(f"   Only {result.updated} needs re-embedding.")

        (source / "warranty.md").unlink()
        result = run(source, state)
        report("4. Deleted one document", result)
        print(f"   {result.deleted} must also be removed from the vector store.")
        print("   Skip this and the assistant keeps quoting a policy that no longer exists.")


if __name__ == "__main__":
    main()
