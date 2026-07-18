"""
Beginner example: Python fundamentals you'll use constantly in AI work.

No third-party dependencies -- pure Python standard library.

Covers: list/dict comprehensions, unpacking, *args/**kwargs, and a simple
class -- all demonstrated on small text-processing tasks, because "process
a batch of text" is the single most common operation in GenAI code.

Run it with:
    python 01_beginner_python_fundamentals.py
"""

DOCUMENTS = [
    "the quick brown fox jumps over the lazy dog",
    "machine learning models learn patterns from data",
    "generative ai models generate new content from patterns",
    "the lazy dog sleeps while the fox jumps",
]


# ---------------------------------------------------------------------------
# List comprehensions -- build a new list from an existing iterable in one line.
# You'll use this constantly to transform API results or dataset rows.
# ---------------------------------------------------------------------------
def demo_list_comprehensions() -> None:
    print("=" * 70)
    print("List comprehensions")
    print("=" * 70)

    word_counts = [len(doc.split()) for doc in DOCUMENTS]
    print(f"Word count per document: {word_counts}")

    long_docs = [doc for doc in DOCUMENTS if len(doc.split()) > 7]
    print(f"Documents with >7 words: {long_docs}")

    upper_first_word = [doc.split()[0].upper() for doc in DOCUMENTS]
    print(f"First word of each doc, uppercased: {upper_first_word}")


# ---------------------------------------------------------------------------
# Dict comprehensions -- build a lookup table in one line. This is exactly
# the pattern you'll use to turn a list of API results into an id -> object
# map, or to count word frequencies (as below).
# ---------------------------------------------------------------------------
def demo_dict_comprehensions() -> None:
    print("\n" + "=" * 70)
    print("Dict comprehensions")
    print("=" * 70)

    doc_lengths = {f"doc_{i}": len(doc.split()) for i, doc in enumerate(DOCUMENTS)}
    print(f"Doc-id -> word-count map: {doc_lengths}")

    # Word frequency across ALL documents combined.
    all_words = " ".join(DOCUMENTS).split()
    word_freq: dict[str, int] = {}
    for word in all_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    print(f"Word frequencies: {word_freq}")

    top_5_words = dict(sorted(word_freq.items(), key=lambda kv: kv[1], reverse=True)[:5])
    print(f"Top 5 most frequent words: {top_5_words}")


# ---------------------------------------------------------------------------
# Unpacking and *args/**kwargs -- you'll see this constantly in API wrapper
# functions that need to accept flexible keyword arguments and forward them.
# ---------------------------------------------------------------------------
def summarize_stats(*numbers: float, **labels: str) -> dict:
    """Accepts any number of positional numbers and any number of
    keyword labels, and returns basic stats. Mirrors the shape of a
    real "call an API with flexible options" function."""
    return {
        "count": len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "avg": sum(numbers) / len(numbers),
        "labels": labels,
    }


def demo_args_kwargs() -> None:
    print("\n" + "=" * 70)
    print("*args / **kwargs")
    print("=" * 70)

    lengths = [len(doc.split()) for doc in DOCUMENTS]
    stats = summarize_stats(*lengths, dataset="demo_docs", unit="words")
    print(f"Stats over word counts: {stats}")

    first, *rest = DOCUMENTS  # unpacking: first element vs. the rest
    print(f"\nFirst document: {first!r}")
    print(f"Remaining {len(rest)} documents (truncated): {rest[0][:30]!r}...")


# ---------------------------------------------------------------------------
# A simple class -- the reuse boundary you'll use for anything stateful,
# like a chat session that needs to remember conversation history.
# ---------------------------------------------------------------------------
class DocumentStore:
    """A minimal in-memory store, mirroring the shape of a real
    (much fancier) vector database client you'll meet in Track 3."""

    def __init__(self) -> None:
        self._docs: list[str] = []

    def add(self, text: str) -> None:
        self._docs.append(text)

    def search(self, keyword: str) -> list[str]:
        """Naive keyword search -- Track 3 replaces this with real
        semantic search over vector embeddings."""
        return [doc for doc in self._docs if keyword.lower() in doc.lower()]

    def __len__(self) -> int:
        return len(self._docs)


def demo_class() -> None:
    print("\n" + "=" * 70)
    print("A simple class: DocumentStore")
    print("=" * 70)

    store = DocumentStore()
    for doc in DOCUMENTS:
        store.add(doc)

    print(f"Store now holds {len(store)} documents.")
    results = store.search("fox")
    print(f"Search results for 'fox': {results}")


def main() -> None:
    demo_list_comprehensions()
    demo_dict_comprehensions()
    demo_args_kwargs()
    demo_class()


if __name__ == "__main__":
    main()
