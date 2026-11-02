"""Lesson 2: the agent loop, written out with nothing hidden.

An "agent" is a while loop: call the model, run what it asks for, append the result, repeat.

Run: python lessons/02_agent_loop.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import get_llm  # noqa: E402
from project.agent import SYSTEM_PROMPT  # noqa: E402
from project.mock_brain import scripted_brain  # noqa: E402
from project.tools import build_registry  # noqa: E402

MESSAGE = "Hi, can I get a refund for order A-1003?"


def main() -> None:
    llm = get_llm(mock_handler=scripted_brain)
    registry = build_registry()
    tools = registry.schemas()
    messages = [{"role": "user", "content": MESSAGE}]
    print(f"USER: {MESSAGE}\n")

    for turn in range(1, 7):
        response = llm.complete(messages, system=SYSTEM_PROMPT, tools=tools, max_tokens=400)

        if not response.tool_calls:
            print(f"Turn {turn}: the model replied with no tool calls, so the loop ends.")
            print(f"\nASSISTANT: {response.text}")
            break

        messages.append(response.as_message())
        for call in response.tool_calls:
            print(f"Turn {turn}: the model asks for {call.name}({call.arguments})")
            result = registry.execute(call.name, call.arguments)
            print(f"         your code returns {result[:110]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "name": call.name, "content": result})


if __name__ == "__main__":
    main()
