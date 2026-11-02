from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def _table_to_text(table):
    rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
    if not rows:
        return ""
    lines = [" | ".join(rows[0]), " | ".join("---" for _ in rows[0])]
    lines.extend(" | ".join(row) for row in rows[1:])
    return "\n".join(lines)


def extract_docx(docx_path):
    """Word files have no fixed pages, so the whole document is one 'page'.

    Headings become Markdown headings, so the chunker can split on them.
    """
    document = Document(docx_path)
    parts = []

    # iter_inner_content keeps paragraphs and tables in reading order.
    for block in document.iter_inner_content():
        if isinstance(block, Table):
            parts.append(_table_to_text(block))
        elif isinstance(block, Paragraph) and block.text.strip():
            style = block.style.name if block.style is not None else ""
            if style.startswith("Heading"):
                level = style.replace("Heading", "").strip()
                prefix = "#" * (int(level) if level.isdigit() else 1)
                parts.append(f"{prefix} {block.text.strip()}")
            else:
                parts.append(block.text.strip())

    return [{"page_number": 1, "content": "\n\n".join(parts)}]


if __name__ == "__main__":
    pages = extract_docx("data/raw/docx/onboarding_guide.docx")
    print(pages[0]["content"][:500])
