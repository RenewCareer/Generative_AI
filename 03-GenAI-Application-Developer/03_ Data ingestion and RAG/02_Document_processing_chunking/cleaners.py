"""Text cleaning. Every rule must be safe: when in doubt, keep the text."""

import re
import unicodedata
from collections import Counter


def normalize_unicode(text: str) -> str:
    """Turn ligatures and non-breaking spaces into plain characters, and drop control codes."""
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")


def fix_hyphenation(text: str) -> str:
    """Rejoin words split across PDF lines: 'manage-\\nment' becomes 'management'."""
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def normalize_whitespace(text: str) -> str:
    """Collapse runs of spaces and blank lines, while keeping paragraph breaks."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    return normalize_whitespace(fix_hyphenation(normalize_unicode(text)))


def _signature(line: str) -> str:
    """Compare lines without digits, so 'Page 3' and 'Page 4' count as the same line."""
    return re.sub(r"\d+", "#", line.strip().lower())


def remove_repeated_lines(pages: list[str], min_share: float = 0.5, edge_lines: int = 2) -> list[str]:
    """Remove headers and footers: short lines repeating at the page edges of most pages."""
    if len(pages) < 3:
        return pages
    counts: Counter[str] = Counter()
    for page in pages:
        lines = [line for line in page.splitlines() if line.strip()]
        counts.update({_signature(line) for line in lines[:edge_lines] + lines[-edge_lines:]})
    threshold = len(pages) * min_share
    boilerplate = {signature for signature, count in counts.items() if count >= threshold and len(signature) < 100}

    cleaned = []
    for page in pages:
        lines = page.splitlines()
        non_empty = [index for index, line in enumerate(lines) if line.strip()]
        edges = set(non_empty[:edge_lines] + non_empty[-edge_lines:])
        cleaned.append(
            "\n".join(
                line for index, line in enumerate(lines) if not (index in edges and _signature(line) in boilerplate)
            )
        )
    return cleaned
