"""Example application: Knowledge Base Ingestor.

Pulls documents from files into one validated format. Bad records go to quarantine rather
than crashing the run, and re-runs only process what changed.

Run: python project/ingest.py
     python project/ingest.py --source path/to/folder --state output/kb
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from collections.abc import Callable, Iterable
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pymupdf
import requests
from pydantic import BaseModel, Field, ValidationError, field_validator

from genai_kit import COURSE_DATA
from genai_kit.retrieval import parse_front_matter

MIN_TEXT_CHARS = 20


class SourceDocument(BaseModel):
    """The contract every source must meet before entering the pipeline."""

    doc_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_type: str
    title: str = ""
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def text_must_have_content(cls, value: str) -> str:
        if len(value.strip()) < MIN_TEXT_CHARS:
            raise ValueError(f"text is shorter than {MIN_TEXT_CHARS} characters")
        return value

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


Record = dict[str, Any]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_text(path: Path) -> list[Record]:
    metadata, body = parse_front_matter(path.read_text(encoding="utf-8"))
    return [
        {
            "doc_id": slug(path.stem),
            "source": path.name,
            "source_type": path.suffix.lstrip("."),
            "title": metadata.pop("title", path.stem),
            "text": body,
            "metadata": metadata,
        }
    ]


def load_csv(path: Path, id_column: str = "", text_column: str = "") -> list[Record]:
    """One document per row. The text column defaults to the column with the longest values."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return []
    columns = list(rows[0])
    id_column = id_column or columns[0]
    text_column = text_column or max(columns, key=lambda column: sum(len(row[column] or "") for row in rows))
    return [
        {
            "doc_id": f"{slug(path.stem)}-{slug(row[id_column])}",
            "source": path.name,
            "source_type": "csv",
            "title": str(row[id_column]),
            "text": row[text_column] or "",
            "metadata": {key: value for key, value in row.items() if key != text_column},
        }
        for row in rows
    ]


def load_json(path: Path, id_key: str = "") -> list[Record]:
    """One document per object. Structured fields become readable 'key: value' text."""
    records = json.loads(path.read_text(encoding="utf-8"))
    records = records if isinstance(records, list) else [records]
    return [_record_from_object(record, path.name, "json", path.stem, id_key) for record in records]


def _record_from_object(record: dict, source: str, source_type: str, prefix: str, id_key: str = "") -> Record:
    key = id_key or next(iter(record))
    return {
        "doc_id": f"{slug(prefix)}-{slug(str(record[key]))}",
        "source": source,
        "source_type": source_type,
        "title": str(record[key]),
        "text": "\n".join(f"{name}: {value}" for name, value in record.items()),
        "metadata": dict(record),
    }


def load_pdf(path: Path) -> list[Record]:
    """One document per page, so citations can point at a page number."""
    records = []
    with pymupdf.open(path) as document:
        for number, page in enumerate(document, start=1):
            records.append(
                {
                    "doc_id": f"{slug(path.stem)}-p{number}",
                    "source": path.name,
                    "source_type": "pdf",
                    "title": path.stem,
                    "text": page.get_text("text", sort=True),
                    "metadata": {"page": number},
                }
            )
    return records


def load_api(url: str, source: str = "api", timeout: float = 10.0) -> list[Record]:
    """Fetch a JSON list from an API. Always set a timeout: the default is to wait forever."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return [_record_from_object(record, url, "api", source) for record in response.json()]


def load_sqlite(database: Path | str, query: str, source: str = "database") -> list[Record]:
    # sqlite3's own context manager commits but does not close, so close explicitly.
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query).fetchall()
    return [_record_from_object(dict(row), str(source), "database", source) for row in rows]


LOADERS: dict[str, Callable[[Path], list[Record]]] = {
    ".txt": load_text,
    ".md": load_text,
    ".csv": load_csv,
    ".json": load_json,
    ".pdf": load_pdf,
}


@dataclass
class ValidationReport:
    valid: list[SourceDocument] = field(default_factory=list)
    quarantined: list[dict[str, Any]] = field(default_factory=list)


def validate_records(records: Iterable[Record]) -> ValidationReport:
    """Good records pass. Bad ones are kept with a reason, so someone can fix the source."""
    report = ValidationReport()
    seen: set[str] = set()
    for record in records:
        try:
            document = SourceDocument.model_validate(record)
            if document.doc_id in seen:
                raise ValueError(f"duplicate doc_id {document.doc_id!r}")
            seen.add(document.doc_id)
            report.valid.append(document)
        except (ValidationError, ValueError) as error:
            reason = (
                "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors())
                if isinstance(error, ValidationError)
                else str(error)
            )
            report.quarantined.append({"record": record, "reason": reason})
    return report


def discover(source: Path) -> tuple[list[Record], list[dict[str, Any]]]:
    """Run the right loader for each file. A corrupt file must not stop the others."""
    records: list[Record] = []
    failures: list[dict[str, Any]] = []
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            failures.append({"record": {"source": path.name}, "reason": f"unsupported type {path.suffix}"})
            continue
        try:
            records.extend(loader(path))
        except Exception as error:
            failures.append({"record": {"source": path.name}, "reason": f"load failed: {error}"})
    return records, failures


@dataclass
class SyncResult:
    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    quarantined: int = 0


def sync(documents: list[SourceDocument], quarantined: list[dict[str, Any]], state_dir: Path) -> SyncResult:
    """Idempotent load: content hashes decide what actually needs re-processing."""
    state_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = state_dir / "manifest.json"
    manifest: dict[str, str] = (
        json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    )

    result = SyncResult(quarantined=len(quarantined))
    current: dict[str, str] = {}
    changed: list[SourceDocument] = []
    for document in documents:
        current[document.doc_id] = document.content_hash
        previous = manifest.get(document.doc_id)
        if previous is None:
            result.added.append(document.doc_id)
            changed.append(document)
        elif previous != document.content_hash:
            result.updated.append(document.doc_id)
            changed.append(document)
        else:
            result.unchanged.append(document.doc_id)
    result.deleted = sorted(set(manifest) - set(current))

    stamp = datetime.now(timezone.utc).isoformat()
    with (state_dir / "documents.jsonl").open("a", encoding="utf-8") as handle:
        for document in changed:
            row = {**document.model_dump(), "content_hash": document.content_hash, "ingested_at": stamp}
            handle.write(json.dumps(row) + "\n")
    with (state_dir / "quarantine.jsonl").open("a", encoding="utf-8") as handle:
        for item in quarantined:
            handle.write(json.dumps({**item, "at": stamp}, default=str) + "\n")
    manifest_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return result


def run(source: Path, state_dir: Path) -> SyncResult:
    records, failures = discover(source)
    report = validate_records(records)
    return sync(report.valid, report.quarantined + failures, state_dir)


def main() -> None:
    unit = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=COURSE_DATA / "docs")
    parser.add_argument("--state", type=Path, default=unit / "output" / "kb")
    args = parser.parse_args()

    result = run(args.source, args.state)
    print(f"Source : {args.source}")
    print(f"Added  : {len(result.added)}  {result.added}")
    print(f"Updated: {len(result.updated)}  {result.updated}")
    print(f"Same   : {len(result.unchanged)}")
    print(f"Deleted: {len(result.deleted)}  {result.deleted}")
    print(f"Quarantined: {result.quarantined}")
    print(f"State in {args.state}. Run again: everything should be unchanged.")


if __name__ == "__main__":
    main()
