import json
from pathlib import Path

import pytest

from chunkers import STRATEGIES, fixed_size_chunks, heading_chunks, sentence_chunks
from cleaners import clean_text, remove_repeated_lines
from make_samples import make_docx, make_xlsx
from pipeline import process_file, run_pipeline
from src.extractors.docx_extractors import extract_docx
from src.extractors.html_extractors import extract_html
from src.extractors.spreadsheet_extractor import extract_spreadsheet

UNIT = Path(__file__).resolve().parents[1]
HTML = UNIT / "data" / "raw" / "html" / "shipping_faq.html"


def test_clean_text_fixes_common_extraction_damage():
    cleaned = clean_text("The ﬁrst   manage-\nment rule​.\n\n\n\nNext.")
    assert cleaned == "The first management rule.\n\nNext."


def test_remove_repeated_lines_keeps_body():
    bodies = ["Risk is measured.", "Teams review it.", "Owners act on it.", "Audits confirm it."]
    pages = [f"HEADER\n{body}\nPage {n}" for n, body in enumerate(bodies, start=1)]
    cleaned = remove_repeated_lines(pages)
    assert cleaned == bodies


def test_remove_repeated_lines_leaves_short_documents_alone():
    pages = ["A\nB", "A\nC"]
    assert remove_repeated_lines(pages) == pages


def test_docx_keeps_headings_and_tables(tmp_path):
    path = tmp_path / "a.docx"
    make_docx(path)
    content = extract_docx(path)[0]["content"]
    assert "# New Hire Onboarding Guide" in content
    assert "IT help desk | it@acme.example" in content
    assert content.index("Key contacts") < content.index("IT help desk") < content.index("Probation")


def test_html_removes_noise():
    content = extract_html(HTML)[0]["content"]
    assert "## How long does delivery take?" in content
    assert "Standard | 3-5 days" in content
    assert "- Dispatch date" in content
    for noise in ("trackVisitor", "newsletter", "Cart", "color: red"):
        assert noise not in content


def test_spreadsheet_rows_keep_column_names(tmp_path):
    path = tmp_path / "a.xlsx"
    make_xlsx(path)
    pages = extract_spreadsheet(path)
    assert len(pages) == 2
    assert "product: Aurora X2" in pages[0]["content"]
    assert "Sheet: Stores" in pages[1]["content"]


def test_fixed_chunks_overlap_and_guard():
    chunks = fixed_size_chunks("abcdefghij" * 5, size=20, overlap=5)
    assert chunks[0][-5:] == chunks[1][:5]
    with pytest.raises(ValueError):
        fixed_size_chunks("x", size=5, overlap=5)


def test_sentence_chunks_never_cut_sentences():
    chunks = sentence_chunks("One is here. Two is here. Three is here.", size=20)
    assert all(chunk.endswith(".") for chunk in chunks)


def test_heading_chunks_carry_path():
    chunks = heading_chunks("# Policy\n## Meals\nUp to 60 dollars.\n## Hotels\nUp to 180 dollars.")
    assert chunks == ["Policy > Meals\nUp to 60 dollars.", "Policy > Hotels\nUp to 180 dollars."]


def test_every_strategy_keeps_all_words():
    text = "# Title\n\n" + " ".join(f"word{i}." for i in range(300))
    for strategy in STRATEGIES.values():
        joined = " ".join(strategy(text, 200, 20))
        assert all(f"word{i}" in joined for i in range(300))


def test_process_file_produces_valid_records():
    records = process_file(HTML)
    assert records and records[0].source_type == "html" and records[0].chunk_id.startswith("shipping-faq#")
    with pytest.raises(ValueError):
        process_file(HTML, strategy="magic")


def test_run_pipeline_isolates_bad_file(tmp_path):
    source = tmp_path / "in"
    source.mkdir()
    (source / "good.html").write_text(HTML.read_text("utf-8"), encoding="utf-8")
    (source / "bad.xlsx").write_text("not a spreadsheet", encoding="utf-8")
    output = tmp_path / "out" / "chunks.jsonl"
    report = run_pipeline(source, output)
    assert report.files_processed == 1 and len(report.files_failed) == 1
    rows = [json.loads(line) for line in output.read_text("utf-8").splitlines()]
    assert len(rows) == report.chunks > 0
