"""extract -> clean -> chunk -> validate, for any supported file type."""

import re
from pathlib import Path

from chunkers import STRATEGIES
from cleaners import clean_text, remove_repeated_lines
from schemas import ChunkRecord, PipelineReport
from src.extractors.docx_extractors import extract_docx
from src.extractors.html_extractors import extract_html
from src.extractors.pdf_extractor import extract_pdf
from src.extractors.spreadsheet_extractor import extract_spreadsheet

EXTRACTORS = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".html": extract_html,
    ".htm": extract_html,
    ".xlsx": extract_spreadsheet,
    ".csv": extract_spreadsheet,
}


def make_doc_id(path):
    return re.sub(r"[^a-z0-9]+", "-", Path(path).stem.lower()).strip("-")


def process_file(path, strategy="heading", size=800, overlap=100):
    path = Path(path)
    extractor = EXTRACTORS.get(path.suffix.lower())
    if extractor is None:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy {strategy!r}. Choose from {sorted(STRATEGIES)}")

    pages = extractor(path)
    contents = remove_repeated_lines([page["content"] for page in pages])
    doc_id = make_doc_id(path)

    records = []
    for page, content in zip(pages, contents):
        cleaned = clean_text(content)
        if not cleaned:
            continue  # Blank or image-only pages. Scanned PDFs would need OCR here.
        for text in STRATEGIES[strategy](cleaned, size, overlap):
            index = len(records)
            records.append(
                ChunkRecord(
                    chunk_id=f"{doc_id}#{index}",
                    doc_id=doc_id,
                    source=path.name,
                    source_type=path.suffix.lstrip(".").lower(),
                    page_number=page["page_number"],
                    chunk_index=index,
                    strategy=strategy,
                    text=text,
                    char_count=len(text),
                )
            )
    return records


def run_pipeline(input_dir, output_path, strategy="heading", size=800, overlap=100):
    """Process a whole folder. One bad file is reported and does not stop the rest."""
    report = PipelineReport()
    all_records = []

    for path in sorted(Path(input_dir).rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTRACTORS:
            continue
        try:
            all_records.extend(process_file(path, strategy, size, overlap))
            report.files_processed += 1
        except Exception as error:
            report.files_failed.append(f"{path.name}: {error}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in all_records:
            handle.write(record.model_dump_json() + "\n")

    report.chunks = len(all_records)
    if all_records:
        report.average_chunk_chars = round(sum(r.char_count for r in all_records) / len(all_records), 1)
    return report
