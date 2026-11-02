"""Lesson 4: combining modalities on a real PDF. Use text where you can, vision where you must.

Vision calls cost more than text. This inspects every page of the NIST PDF and routes each to
the cheapest method that will work.

Run: python lessons/04_document_vision_routing.py
"""

import sys
from collections import Counter
from pathlib import Path

import pymupdf

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

PDF = UNIT.parent / "03_ Data ingestion and RAG" / "02_Document_processing_chunking" / "data" / "raw" / "pdf" / "NIST.AI.100-1.pdf"
MIN_TEXT_CHARS = 200
IMAGE_AREA_FOR_VISION = 0.15


def route_page(text_chars: int, image_area_share: float) -> str:
    has_figure = image_area_share >= IMAGE_AREA_FOR_VISION
    if text_chars < MIN_TEXT_CHARS:
        return "vision" if has_figure else "skip"
    return "text+vision" if has_figure else "text"


def analyse_page(page: pymupdf.Page) -> tuple[int, float]:
    """Measure text length, and the share of the page covered by raster images.

    This does not detect figures drawn as vector graphics: those would need a rule of their
    own, because many PDFs (including this one) put a full-page background shape on each page.
    """
    images = sum(abs(pymupdf.Rect(info["bbox"]) & page.rect) for info in page.get_image_info())
    return len(page.get_text("text").strip()), min(images / abs(page.rect), 1.0)


def main() -> None:
    if not PDF.exists():
        print(f"Sample PDF not found at {PDF}. Copy any PDF there to try this lesson.")
        return

    routes: Counter[str] = Counter()
    example: tuple[int, str] | None = None
    with pymupdf.open(PDF) as document:
        for number, page in enumerate(document, start=1):
            chars, share = analyse_page(page)
            route = route_page(chars, share)
            routes[route] += 1
            if route in ("vision", "text+vision") and example is None:
                example = (number, route)
                output = UNIT / "output" / f"page_{number}.png"
                output.parent.mkdir(exist_ok=True)
                page.get_pixmap(dpi=120).save(output)
        total = len(document)

    print(f"{total} pages inspected. Routing:")
    for route, count in routes.most_common():
        print(f"  {route:<14}{count:>4} pages")
    if example:
        print(f"\nFirst figure-heavy page: {example[0]} ({example[1]}). Rendered to output/page_{example[0]}.png")
    print(f"\nSending only these pages to vision avoids {routes['text'] + routes['skip']} needless vision calls.")


if __name__ == "__main__":
    main()
