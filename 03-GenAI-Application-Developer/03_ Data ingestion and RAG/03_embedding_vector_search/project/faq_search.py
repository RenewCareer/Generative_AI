"""Example application: FAQ Search, a persistent semantic search engine on FAISS.

Run:
    python project/faq_search.py build
    python project/faq_search.py search "how long is the warranty"
    python project/faq_search.py search "annual leave" --access internal
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from genai_kit import Chunk, Embedder, SearchHit, get_embedder, load_course_chunks

INDEX_DIR = Path(__file__).resolve().parents[1] / "output" / "faq_index"
OVERFETCH = 4  # Fetch extra candidates, because filtering happens after the search.


class FaissStore:
    """A vector store with a small interface, so it can be swapped for a hosted service."""

    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder
        self.index: faiss.Index | None = None
        self.chunks: list[Chunk] = []

    def build(self, chunks: list[Chunk]) -> None:
        vectors = self.embedder.embed([chunk.text for chunk in chunks]).astype(np.float32)
        # Normalised vectors make inner product equal to cosine similarity.
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.chunks = chunks

    def search(self, query: str, k: int = 3, access: str | None = None) -> list[SearchHit]:
        if self.index is None:
            raise RuntimeError("The index is empty. Build or load it first.")
        fetch = len(self.chunks) if access else min(k * OVERFETCH, len(self.chunks))
        scores, ids = self.index.search(self.embedder.embed([query]).astype(np.float32), fetch)
        hits = []
        for score, position in zip(scores[0], ids[0]):
            chunk = self.chunks[int(position)]
            if access is None or chunk.metadata.get("access") == access:
                hits.append(SearchHit(chunk, float(score)))
            if len(hits) == k:
                break
        return hits

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        # serialize + tofile handles paths with spaces and non-ASCII characters on Windows.
        faiss.serialize_index(self.index).tofile(directory / "index.faiss")
        with (directory / "chunks.jsonl").open("w", encoding="utf-8") as handle:
            for chunk in self.chunks:
                handle.write(json.dumps(asdict(chunk)) + "\n")
        # Record the model: vectors from different models must never be mixed.
        (directory / "meta.json").write_text(json.dumps({"embedder": self.embedder.name}), encoding="utf-8")

    def load(self, directory: Path) -> None:
        meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
        if meta["embedder"] != self.embedder.name:
            raise ValueError(
                f"Index was built with {meta['embedder']} but the current embedder is "
                f"{self.embedder.name}. Rebuild the index."
            )
        self.index = faiss.deserialize_index(np.fromfile(directory / "index.faiss", dtype=np.uint8))
        with (directory / "chunks.jsonl").open(encoding="utf-8") as handle:
            self.chunks = [Chunk(**json.loads(line)) for line in handle]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build")
    search_parser = commands.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("-k", type=int, default=3)
    search_parser.add_argument("--access", choices=["public", "internal"])
    args = parser.parse_args()

    store = FaissStore(get_embedder())
    if args.command == "build":
        store.build(load_course_chunks())
        store.save(INDEX_DIR)
        print(f"Indexed {len(store.chunks)} chunks with '{store.embedder.name}' in {INDEX_DIR}")
        return

    store.load(INDEX_DIR)
    for rank, hit in enumerate(store.search(args.query, args.k, args.access), start=1):
        preview = " ".join(hit.chunk.text.split())[:110]
        print(f"{rank}. [{hit.score:.3f}] {hit.chunk.id}\n   {preview}...")


if __name__ == "__main__":
    main()
