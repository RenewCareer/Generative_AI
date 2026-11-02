"""Example application: Policy Assistant, answering from company documents with citations.

Run:
    python project/policy_assistant.py --question "How many days do customers have to return an item?"
    python project/policy_assistant.py        (interactive)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.rag import RagAnswer, default_pipeline  # noqa: E402


def render(result: RagAnswer) -> str:
    lines = [result.answer]
    if result.refused:
        lines.append("\n(No supporting document was found.)")
    if result.cited:
        lines.append("\nSources:")
        for number in result.cited:
            hit = result.sources[number - 1]
            lines.append(f"  [{number}] {hit.chunk.metadata.get('title', hit.chunk.doc_id)} ({hit.chunk.id})")
    if result.invalid_citations:
        lines.append(f"\nWarning: the model cited sources that do not exist: {result.invalid_citations}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question")
    args = parser.parse_args()

    pipeline = default_pipeline()
    print(f"Loaded {len(pipeline.index.chunks)} chunks.")

    if args.question:
        print(render(pipeline.ask(args.question)))
        return

    print("Ask about Acme Retail policies. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            return
        if question:
            print(render(pipeline.ask(question)))


if __name__ == "__main__":
    main()
