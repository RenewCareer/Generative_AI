"""Lesson 3: never trust a citation you have not checked.

Models can invent a source number. The pipeline compares every citation against what it
actually retrieved. This scripted model cites a source that does not exist.

Run: python lessons/03_citations_you_can_verify.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, VectorIndex, load_course_chunks  # noqa: E402
from project.policy_assistant import render  # noqa: E402
from project.rag import RagPipeline  # noqa: E402


def main() -> None:
    index = VectorIndex().add(load_course_chunks())

    honest = RagPipeline(index, MockClient())
    print("A correct citation:")
    print(render(honest.ask("What is the hotel limit per night?")))

    def hallucinating(messages, system, tools):
        return "Hotels are reimbursed up to 180 dollars per night [1], as confirmed by the CFO [9]."

    print("\n" + "-" * 60 + "\nA model that invents source [9]:")
    print(render(RagPipeline(index, MockClient(hallucinating)).ask("What is the hotel limit per night?")))


if __name__ == "__main__":
    main()
