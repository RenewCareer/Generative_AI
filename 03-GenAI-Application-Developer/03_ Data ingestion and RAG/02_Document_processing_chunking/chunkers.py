"""Chunking strategies. Each takes text and returns a list of chunk strings."""

import re

from genai_kit import recursive_chunk


def fixed_size_chunks(text, size=500, overlap=50):
    """Simple and predictable, but cuts through words and sentences."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    step = size - overlap
    return [text[start : start + size].strip() for start in range(0, len(text), step) if text[start:].strip()]


def recursive_chunks(text, size=500, overlap=50):
    """The sensible default: prefers headings, then paragraphs, then sentences."""
    return recursive_chunk(text, max_chars=size, overlap=overlap)


def sentence_chunks(text, size=500, overlap=0):
    """Whole sentences only, packed up to the size limit."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > size:
            chunks.append(current.strip())
            current = ""
        current += sentence + " "
    if current.strip():
        chunks.append(current.strip())
    return chunks


def heading_chunks(text, size=500, overlap=50):
    """Split on Markdown headings and prefix each chunk with its heading path.

    "up to 60 dollars per day" is much easier to retrieve when the chunk also says
    "Travel and Expense Policy > Meals".
    """
    path = {}
    sections = []
    current = []

    def flush():
        body = "\n".join(current).strip()
        if body:
            trail = " > ".join(path[level] for level in sorted(path))
            sections.append((trail, body))
        current.clear()

    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)", line)
        if match:
            flush()
            level = len(match.group(1))
            path = {key: value for key, value in path.items() if key < level}
            path[level] = match.group(2).strip()
        else:
            current.append(line)
    flush()

    if not sections:
        return recursive_chunks(text, size, overlap)

    chunks = []
    for trail, body in sections:
        for piece in recursive_chunks(body, size, overlap):
            chunks.append(f"{trail}\n{piece}" if trail else piece)
    return chunks


STRATEGIES = {
    "fixed": fixed_size_chunks,
    "recursive": recursive_chunks,
    "sentence": sentence_chunks,
    "heading": heading_chunks,
}
