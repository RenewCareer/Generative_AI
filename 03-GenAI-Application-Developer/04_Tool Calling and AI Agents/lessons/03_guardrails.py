"""Lesson 3: guardrails for autonomy. Assume that the model will sometimes do the wrong thing.

Run: python lessons/03_guardrails.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import LLMResponse, MockClient, ToolCall  # noqa: E402
from project.agent import Agent  # noqa: E402
from project.mock_brain import scripted_brain  # noqa: E402
from project.tools import build_registry  # noqa: E402


def stuck_model(messages, system, tools) -> LLMResponse:
    """A model that keeps calling the same tool forever."""
    return LLMResponse("", "mock", "mock", tool_calls=[ToolCall("c", "search_policies", {"query": "refund"})])


def reckless_model(messages, system, tools) -> str | LLMResponse:
    """A model that skips the eligibility check, and tries to refund an ineligible order."""
    if any(message["role"] == "tool" for message in messages):
        return messages[-1]["content"][:120]
    return LLMResponse("", "mock", "mock", tool_calls=[ToolCall("c", "issue_refund", {"order_id": "A-1003", "reason": "x"})])


def main() -> None:
    print("1. HUMAN APPROVAL: a refund needs a person, and the default answer is no")
    result = Agent(MockClient(scripted_brain), build_registry()).run("Refund order A-1001")
    print(f"   Approver said no. Agent: {result.answer}")
    registry = build_registry()
    result = Agent(MockClient(scripted_brain), registry, approver=lambda call: True).run("Refund order A-1001")
    print(f"   Approver said yes. Agent: {result.answer}\n")

    print("2. STEP LIMIT: a stuck model cannot loop or spend forever")
    result = Agent(MockClient(stuck_model), build_registry(), max_steps=3).run("anything")
    print(f"   Stopped: {result.stop_reason} after {len(result.steps)} tool calls\n")

    print("3. TOOLS ENFORCE THE RULES: the code blocks a bad refund, even when approved")
    registry = build_registry()
    result = Agent(MockClient(reckless_model), registry, approver=lambda call: True).run("Refund A-1003")
    print(f"   Tool said: {result.steps[0].result}")
    print(f"   Money moved: {registry.refunds}\n")

    print("4. LEAST PRIVILEGE: a read-only agent does not even know that refunds exist")
    agent = Agent(MockClient(scripted_brain), build_registry(), tool_names=["get_order", "search_policies"])
    print(f"   Tools offered: {[tool['name'] for tool in agent.registry.schemas(agent.tool_names)]}")


if __name__ == "__main__":
    main()
