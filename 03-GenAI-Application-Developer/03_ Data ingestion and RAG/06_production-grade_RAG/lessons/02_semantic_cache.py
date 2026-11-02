"""Lesson 2: semantic caching saves money, but must respect permissions and freshness.

Run: python lessons/02_semantic_cache.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import Chunk, MockClient, load_course_chunks  # noqa: E402
from project.pipeline import ProductionRag  # noqa: E402


class CountingLLM(MockClient):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def complete(self, *args, **kwargs):
        self.calls += 1
        return super().complete(*args, **kwargs)


def main() -> None:
    llm = CountingLLM()
    rag = ProductionRag(load_course_chunks(), llm)

    print("Model calls after each request:")
    for question, role in [
        ("What is the hotel limit per night?", "employee"),
        ("what is the hotel limit per night", "employee"),
        ("What is the hotel limit per night?", "customer"),
    ]:
        result = rag.ask(question, role=role)
        print(f"  calls={llm.calls} cached={result.cached!s:<6} role={role:<9} {question}")
    print("  The customer did NOT receive the employee's cached answer: scopes are separate.\n")

    version = rag.index_version
    extra = Chunk("new#0", "new", "Hotel stays are now reimbursed up to 220 dollars per night.", {"access": "internal"})
    rag.reindex([*load_course_chunks(), extra])
    result = rag.ask("What is the hotel limit per night?", role="employee")
    print(f"Index {version} became {rag.index_version}")
    print(f"  calls={llm.calls} cached={result.cached}: the new version invalidated the old answers.")
    print("\nTune the threshold on real traffic: too low, and different questions get the same answer.")


if __name__ == "__main__":
    main()
