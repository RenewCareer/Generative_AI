"""Lesson 4: evaluating the answer, not just the retrieval.

Good retrieval can still produce a bad answer, so we score both. There are cheap checks
that run on every commit, and an LLM judge for what they cannot see.

Run: python lessons/04_answer_evaluation.py
"""

import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import get_llm  # noqa: E402
from project.metrics import contains_all, groundedness  # noqa: E402

CONTEXT = "Hotel stays are reimbursed up to 180 dollars per night. Higher stays need director approval."
EXAMPLES = [
    ("Correct", "Hotels are reimbursed up to 180 dollars per night.", ["180 dollars"]),
    ("Invented fact", "Hotels are reimbursed up to 180 dollars per night. Pets stay free on weekends.", ["180 dollars"]),
    ("Wrong number", "Hotels are reimbursed up to 250 dollars per night.", ["180 dollars"]),
]


class Judgement(BaseModel):
    verdict: Literal["supported", "partially_supported", "not_supported"]
    reason: str


JUDGE_PROMPT = (
    "You are an evaluator. Decide whether every claim in the ANSWER is supported by the "
    "CONTEXT. Do not use outside knowledge."
)


def main() -> None:
    print(f"Context: {CONTEXT}\n")
    print(f"{'case':<16}{'grounded':>10}{'has fact':>10}  answer")
    for name, answer, facts in EXAMPLES:
        print(f"{name:<16}{groundedness(answer, CONTEXT):>10.2f}{contains_all(answer, facts):>10.0f}  {answer}")

    print("\nThe 'Wrong number' case shows the limit of word overlap: groundedness stays high, and")
    print("only the exact fact check catches it. Layer your checks.\n")

    llm = get_llm(
        mock_parse_handler=lambda messages, schema: {
            "verdict": "not_supported",
            "reason": "Mock judge: 250 dollars does not appear in the context.",
        }
    )
    judgement = llm.parse(
        [{"role": "user", "content": f"CONTEXT:\n{CONTEXT}\n\nANSWER:\n{EXAMPLES[2][1]}"}],
        Judgement,
        system=JUDGE_PROMPT,
    )
    print(f"LLM judge on 'Wrong number': {judgement.verdict}. {judgement.reason}")
    print("\nLLM judges cost money and can be wrong too. Check them against human labels first.")


if __name__ == "__main__":
    main()
