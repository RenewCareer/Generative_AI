"""Lesson 1: enforce permissions in retrieval, not in the prompt.

Run: python lessons/01_access_control.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, load_course_chunks  # noqa: E402
from project.pipeline import ProductionRag  # noqa: E402

QUESTION = "How many days of paid annual leave do employees receive?"


def main() -> None:
    rag = ProductionRag(load_course_chunks(), MockClient())
    for role in ("employee", "customer"):
        result = rag.ask(QUESTION, role=role)
        print(f"Role: {role}")
        print(f"  answer : {result.answer}")
        print(f"  sources: {result.sources}\n")
    print("The customer's request never saw the HR document, so the model could not leak it,")
    print("whatever a clever prompt might ask for.")


if __name__ == "__main__":
    main()
