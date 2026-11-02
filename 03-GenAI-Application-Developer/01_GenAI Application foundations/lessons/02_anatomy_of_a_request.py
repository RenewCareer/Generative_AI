"""Lesson 2: what actually goes over the wire in an LLM call.

The model is stateless. Everything it knows must be inside the request.

Run: python lessons/02_anatomy_of_a_request.py
"""

import json

from genai_kit import get_llm

SYSTEM = "You are a GenAI trainer. Answer in one short sentence."
QUESTION = "What is a context window?"


def main() -> None:
    print("REQUEST, the shape sent to OpenAI's Responses API:")
    print(
        json.dumps(
            {
                "model": "<from OPENAI_MODEL>",
                "instructions": SYSTEM,
                "input": [{"role": "user", "content": QUESTION}],
                "max_output_tokens": 100,
            },
            indent=2,
        )
    )

    print("\nThe same request for Anthropic's Messages API:")
    print(
        json.dumps(
            {
                "model": "<from ANTHROPIC_MODEL>",
                "system": SYSTEM,
                "messages": [{"role": "user", "content": QUESTION}],
                "max_tokens": 100,
            },
            indent=2,
        )
    )

    llm = get_llm()
    response = llm.complete([{"role": "user", "content": QUESTION}], system=SYSTEM, max_tokens=100)

    print("\nRESPONSE, the parts your application cares about:")
    print(f"  provider     : {response.provider}")
    print(f"  model        : {response.model}")
    print(f"  text         : {response.text}")
    print(f"  input tokens : {response.usage.input_tokens}")
    print(f"  output tokens: {response.usage.output_tokens}")

    print("\nThe model is stateless. A follow-up only works if we resend the history:")
    history = [
        {"role": "user", "content": QUESTION},
        response.as_message(),
        {"role": "user", "content": "Give an example."},
    ]
    print(f"  Second request carries {len(history)} messages, so input tokens grow on every turn.")


if __name__ == "__main__":
    main()
