"""Lesson 1: a golden-set evaluation catches a regression before your users do.

Run: python lessons/01_eval_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, VectorIndex, load_course_chunks  # noqa: E402
from project.assistant import GuardedAssistant  # noqa: E402
from project.evaluate import evaluate  # noqa: E402


def show(label: str, report) -> None:
    print(label)
    print(f"  accuracy {report.metrics['accuracy']:.0%}, citations {report.metrics['citation_rate']:.0%}")
    print(f"  gate: {'PASS' if report.passed else 'FAIL'} {report.failures or ''}\n")


def main() -> None:
    chunks = load_course_chunks()
    index = VectorIndex().add(chunks)

    show("Version A: healthy", evaluate(GuardedAssistant(MockClient(), index)))

    # A "small" change: someone retrieves fewer chunks to save tokens.
    show("Version B: k reduced to 1 to save money", evaluate(GuardedAssistant(MockClient(), index, k=1)))

    def uncited(messages, system, tools):
        return MockClient().complete(messages).text.split(" [")[0]

    show("Version C: a prompt edit dropped the citation rule", evaluate(GuardedAssistant(MockClient(uncited), index)))

    print("Version B lost accuracy but stayed above the limit: the gate passes, and the score shows")
    print("the cost of that saving, so the team can decide knowingly. Version C is blocked outright.")
    print("In a quick manual test, all three versions would look fine.")


if __name__ == "__main__":
    main()
