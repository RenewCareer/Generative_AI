"""Lesson 4: see inside every request, and stay useful when the provider is down.

Run: python lessons/04_tracing_and_fallback.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, load_course_chunks  # noqa: E402
from project.pipeline import ProductionRag  # noqa: E402

QUESTION = "What is the hotel limit per night?"


class DownLLM(MockClient):
    model = "primary-model"

    def complete(self, *args, **kwargs):
        raise TimeoutError("provider timed out")


def main() -> None:
    chunks = load_course_chunks()

    rag = ProductionRag(chunks, MockClient())
    rag.ask(QUESTION, role="employee")
    print("A TRACE: one record per request, ready to send to your observability tool")
    print(json.dumps(json.loads(rag.last_trace.to_json()), indent=2)[:900], "\n")

    print("FALLBACK LADDER")
    result = ProductionRag(chunks, DownLLM(), fallback_llm=MockClient()).ask(QUESTION, role="employee")
    print(f"  1. Primary down, backup model answers: degraded={result.degraded}\n     {result.answer}")
    result = ProductionRag(chunks, DownLLM()).ask(QUESTION, role="employee")
    print(f"  2. All models down, show the passage: degraded={result.degraded}\n     {result.answer[:150]}...")


if __name__ == "__main__":
    main()
