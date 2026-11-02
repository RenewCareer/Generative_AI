"""Lesson 4: multi-agent routing, the most common multi-agent pattern in production.

A router sends each message to a specialist that holds only the tools it needs. Start with
one agent. Split only when tool lists or instructions grow too large to work reliably.

Run: python lessons/04_router_multi_agent.py
"""

import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import LLMClient, get_llm  # noqa: E402
from project.agent import Agent  # noqa: E402
from project.mock_brain import scripted_brain  # noqa: E402
from project.tools import build_registry  # noqa: E402


class Route(BaseModel):
    specialist: Literal["orders", "policies", "human"]
    reason: str


SPECIALISTS = {
    "orders": ["get_order", "check_refund_eligibility"],
    "policies": ["search_policies"],
    "human": ["escalate_to_human"],
}
ROUTER_PROMPT = (
    "Route the customer message. orders: anything about a specific order. "
    "policies: general questions. human: legal threats or abusive messages."
)


def mock_route(messages, schema) -> dict:
    text = messages[-1]["content"].lower()
    if any(word in text for word in ("lawyer", "sue", "legal")):
        return {"specialist": "human", "reason": "Legal threat"}
    if "a-1" in text:
        return {"specialist": "orders", "reason": "Mentions an order ID"}
    return {"specialist": "policies", "reason": "General question"}


def handle(llm: LLMClient, message: str) -> None:
    route = llm.parse([{"role": "user", "content": message}], Route, system=ROUTER_PROMPT, max_tokens=100)
    tools = SPECIALISTS[route.specialist]
    result = Agent(llm, build_registry(), tool_names=tools).run(message)
    print(f"Customer  : {message}")
    print(f"Router    : {route.specialist} ({route.reason})")
    print(f"Specialist: tools={tools}, used={[step.tool for step in result.steps]}")
    print(f"Reply     : {result.answer[:120]}\n")


def main() -> None:
    llm = get_llm(mock_handler=scripted_brain, mock_parse_handler=mock_route)
    for message in (
        "Where is my order A-1002?",
        "How long does express delivery take?",
        "My lawyer will sue you over this.",
    ):
        handle(llm, message)


if __name__ == "__main__":
    main()
