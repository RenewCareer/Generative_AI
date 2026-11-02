"""Lesson 1: what each extractor gives you, and what real documents look like.

Run: python lessons/01_extract_every_format.py
"""

import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from src.extractors.docx_extractors import extract_docx  # noqa: E402
from src.extractors.html_extractors import extract_html  # noqa: E402
from src.extractors.pdf_extractor import extract_pdf  # noqa: E402
from src.extractors.spreadsheet_extractor import extract_spreadsheet  # noqa: E402

RAW = UNIT / "data" / "raw"


def show(label, pages):
    print(f"===== {label}: {len(pages)} page(s) =====")
    print(pages[0]["content"][:420].strip(), "\n")


def main():
    show("DOCX: headings and tables preserved", extract_docx(RAW / "docx" / "onboarding_guide.docx"))
    show("HTML: navigation, footer and scripts removed", extract_html(RAW / "html" / "shipping_faq.html"))
    show("XLSX: each row keeps its column names", extract_spreadsheet(RAW / "spreadsheets" / "price_list.xlsx"))

    pdf = RAW / "pdf" / "NIST.AI.100-1.pdf"
    if pdf.exists():
        pages = extract_pdf(str(pdf))
        print(f"===== PDF: {len(pages)} pages of the NIST AI Risk Management Framework =====")
        print("Page 12, raw. Spot the broken lines, page furniture and hyphenation:\n")
        print(pages[11]["content"][:500])


if __name__ == "__main__":
    main()
