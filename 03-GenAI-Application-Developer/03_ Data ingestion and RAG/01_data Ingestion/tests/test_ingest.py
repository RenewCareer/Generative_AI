import json
import sqlite3
from pathlib import Path

from genai_kit import COURSE_DATA
from project.ingest import discover, load_csv, load_json, load_sqlite, run, validate_records

TEXT = "This text is long enough to pass validation."


def test_loaders_return_one_shape():
    expected = {"doc_id", "source", "source_type", "title", "text", "metadata"}
    for records in (load_csv(COURSE_DATA / "reviews.csv"), load_json(COURSE_DATA / "orders.json")):
        assert records and set(records[0]) == expected


def test_csv_picks_longest_column_as_text():
    assert "Battery life" in load_csv(COURSE_DATA / "reviews.csv")[0]["text"]


def test_sqlite_loader(tmp_path):
    database = tmp_path / "db.sqlite"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE t (id INTEGER, body TEXT)")
    connection.execute("INSERT INTO t VALUES (1, 'hello world, this is a body')")
    connection.commit()
    connection.close()
    assert load_sqlite(database, "SELECT * FROM t", "x")[0]["doc_id"] == "x-1"


def test_validation_quarantines_with_reasons():
    base = {"source": "a", "source_type": "txt"}
    report = validate_records(
        [
            {**base, "doc_id": "a", "text": TEXT},
            {**base, "doc_id": "a", "text": TEXT},
            {**base, "doc_id": "b", "text": "short"},
        ]
    )
    assert len(report.valid) == 1
    reasons = " ".join(item["reason"] for item in report.quarantined)
    assert "duplicate" in reasons and "shorter" in reasons


def test_bad_files_do_not_stop_discovery(tmp_path):
    (tmp_path / "good.txt").write_text(TEXT, encoding="utf-8")
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    (tmp_path / "image.xyz").write_text("x", encoding="utf-8")
    records, failures = discover(tmp_path)
    assert len(records) == 1 and len(failures) == 2


def test_sync_is_idempotent_and_detects_changes(tmp_path):
    source, state = tmp_path / "source", tmp_path / "state"
    source.mkdir()
    (source / "a.txt").write_text(TEXT, encoding="utf-8")
    (source / "b.txt").write_text(TEXT + " Second.", encoding="utf-8")

    assert sorted(run(source, state).added) == ["a", "b"]
    second = run(source, state)
    assert not second.added and not second.updated and len(second.unchanged) == 2

    (source / "a.txt").write_text(TEXT + " Edited.", encoding="utf-8")
    (source / "b.txt").unlink()
    third = run(source, state)
    assert third.updated == ["a"] and third.deleted == ["b"]

    rows = [json.loads(line) for line in Path(state, "documents.jsonl").read_text("utf-8").splitlines()]
    assert len(rows) == 3
