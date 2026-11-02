"""Lesson 1: all of RAG in about 30 lines. Everything else is refinement.

Run: python lessons/01_rag_in_30_lines.py
"""

from genai_kit import VectorIndex, format_context, get_embedder, get_llm, load_course_chunks

QUESTION = "How many days do customers have to return an item?"


def main() -> None:
    # INDEX: done once, ahead of time
    chunks = load_course_chunks()
    index = VectorIndex(get_embedder()).add(chunks)
    print(f"Indexed {len(chunks)} chunks\n")

    # 1. RETRIEVE: find the passages closest to the question
    hits = index.search(QUESTION, k=3)
    print("RETRIEVED")
    for hit in hits:
        print(f"  {hit.score:.3f}  {hit.chunk.id}")

    # 2. AUGMENT: put those passages into the prompt
    prompt = f"Sources:\n{format_context(hits)}\n\nQuestion: {QUESTION}"
    print(f"\nPROMPT (first 300 characters)\n{prompt[:300]}...\n")

    # 3. GENERATE: the model answers from the supplied text
    response = get_llm().complete(
        [{"role": "user", "content": prompt}],
        system="Answer using only the sources. Cite them like [1].",
    )
    print(f"ANSWER\n{response.text}")


if __name__ == "__main__":
    main()
