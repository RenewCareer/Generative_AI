"""Lesson 3: compare chunking strategies by measuring retrieval, not by guessing.

For each strategy and size: chunk the knowledge base, search with every golden question,
and count how often the top chunk, or the top 3, contain the exact answer text.

Run: python lessons/03_chunking_strategies.py
"""

import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from chunkers import STRATEGIES  # noqa: E402
from genai_kit import Chunk, VectorIndex, load_course_docs  # noqa: E402
from genai_kit.retrieval import load_golden  # noqa: E402


def build_chunks(strategy, size, overlap):
    chunks = []
    for doc in load_course_docs():
        # Prefix the title for every strategy, so the comparison is about splitting alone.
        title = doc["metadata"].get("title", "")
        for number, text in enumerate(STRATEGIES[strategy](doc["text"], size, overlap)):
            chunks.append(Chunk(f"{doc['doc_id']}#{number}", doc["doc_id"], f"{title}\n{text}"))
    return chunks


def answer_hit_rate(chunks, k=3):
    index = VectorIndex().add(chunks)
    golden = load_golden()
    hits = 0
    for item in golden:
        retrieved = " ".join(hit.chunk.text for hit in index.search(item["question"], k=k))
        hits += all(phrase.lower() in retrieved.lower() for phrase in item["must_include"])
    return hits / len(golden)


def main():
    sample = load_course_docs()[1]["text"]
    print("How each strategy cuts the same text (first chunk of 80-character chunks):")
    for name, strategy in STRATEGIES.items():
        print(f"  {name:<10}{strategy(sample, 80, 0)[0]!r}")

    print(f"\n{'strategy':<12}{'size':>6}{'chunks':>8}{'avg chars':>11}{'answer in top 1':>17}{'in top 3':>10}")
    for name in STRATEGIES:
        for size in (150, 300, 600):
            chunks = build_chunks(name, size, size // 10)
            average = sum(len(chunk.text) for chunk in chunks) / len(chunks)
            top1, top3 = answer_hit_rate(chunks, k=1), answer_hit_rate(chunks, k=3)
            print(f"{name:<12}{size:>6}{len(chunks):>8}{average:>11.0f}{top1:>17.0%}{top3:>10.0%}")

    print("\nRead the table with the chunk size in mind. A bigger chunk holds the answer more easily,")
    print("but every chunk you retrieve costs tokens, and an answer buried in a long chunk is harder")
    print("to use. Run this on YOUR documents and YOUR questions: these are 8 short documents, and")
    print("this offline run uses word-overlap embeddings. Rerun with an API key to compare.")


if __name__ == "__main__":
    main()
