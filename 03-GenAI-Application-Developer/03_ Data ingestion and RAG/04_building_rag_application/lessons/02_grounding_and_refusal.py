"""Lesson 2: a RAG system must know when NOT to answer.

Run: python lessons/02_grounding_and_refusal.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.rag import default_pipeline  # noqa: E402

QUESTIONS = [
    ("Answerable", "What is the hotel limit per night?"),
    ("Answerable", "What does error code NB-17 mean?"),
    ("Not in the documents", "Who won the football world cup in 2018?"),
    ("Not in the documents", "What is the CEO's favourite colour?"),
]


def main() -> None:
    pipeline = default_pipeline()
    for kind, question in QUESTIONS:
        result = pipeline.ask(question)
        print(f"{kind}: {question}")
        print(f"  -> {result.answer}")
        print(f"     refused={result.refused}, retrieved={len(result.sources)}\n")

    print("There are two layers of defence:")
    print("  1. A score threshold skips the model when nothing relevant was found.")
    print("  2. The prompt tells the model to refuse if the sources lack the answer.")


if __name__ == "__main__":
    main()
