"""Lesson 3: metadata filters combine meaning with hard business rules.

Run: python lessons/03_metadata_filtering.py
"""

from genai_kit import VectorIndex, get_embedder, load_course_chunks


def show(label, hits) -> None:
    print(label)
    for hit in hits:
        print(f"  {hit.score:.3f}  {hit.chunk.doc_id:<18} access={hit.chunk.metadata['access']:<9}")
    print()


def main() -> None:
    index = VectorIndex(get_embedder()).add(load_course_chunks())
    query = "how many days do employees and customers get"

    show("No filter: searches everything, including internal HR documents", index.search(query, k=4))
    show(
        "Filter access=public: what an external customer may see",
        index.search(query, k=4, where=lambda m: m["access"] == "public"),
    )
    show(
        "Filter department=hr: narrows the search to one team",
        index.search(query, k=4, where=lambda m: m["department"] == "hr"),
    )
    print("Vector databases apply such filters inside the search. Never rely on the prompt to hide")
    print("documents: a filter is a guarantee, and an instruction to the model is not.")


if __name__ == "__main__":
    main()
