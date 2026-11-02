"""Example application: Study Buddy, a small but properly structured Q&A CLI.

Run:
    python project/study_buddy.py --question "What is an embedding?"
    python project/study_buddy.py --question "What is a token?" --stream
    python project/study_buddy.py          (interactive)
"""

from __future__ import annotations

import argparse
import logging
import sys

from genai_kit import LLMClient, LLMResponse, get_llm

logger = logging.getLogger("study_buddy")

SYSTEM_PROMPT = (
    "You are a patient GenAI trainer. Explain technical concepts clearly, step by step, "
    "with one practical example. Keep answers under 150 words. "
    "If you are unsure of something, say so rather than guessing."
)
MAX_QUESTION_CHARS = 2_000


def validate_question(question: str) -> str:
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty.")
    if len(question) > MAX_QUESTION_CHARS:
        raise ValueError(f"Question is too long (limit is {MAX_QUESTION_CHARS} characters).")
    return question


def ask(llm: LLMClient, question: str) -> LLMResponse:
    return llm.complete(
        [{"role": "user", "content": validate_question(question)}],
        system=SYSTEM_PROMPT,
        max_tokens=400,
    )


def answer_once(llm: LLMClient, question: str, stream: bool) -> int:
    try:
        if stream:
            messages = [{"role": "user", "content": validate_question(question)}]
            for delta in llm.stream(messages, system=SYSTEM_PROMPT, max_tokens=400):
                print(delta, end="", flush=True)
            print()
        else:
            response = ask(llm, question)
            print(response.text)
            print(
                f"\n[{response.provider}/{response.model}] "
                f"{response.usage.input_tokens} in, {response.usage.output_tokens} out"
            )
    except ValueError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 2
    except Exception:
        # Log the detail for developers, and show users something safe.
        logger.exception("LLM request failed")
        print("Sorry, the AI service is unavailable. Please try again.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", help="Ask one question and exit")
    parser.add_argument("--stream", action="store_true", help="Print the answer as it is generated")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)

    llm = get_llm()
    if args.question is not None:
        return answer_once(llm, args.question, args.stream)

    print("Study Buddy. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            return 0
        answer_once(llm, question, args.stream)


if __name__ == "__main__":
    sys.exit(main())
