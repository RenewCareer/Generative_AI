"""Example application: Helpdesk Agent, with real tools, human approval and an audit trail.

Run:
    python project/helpdesk_agent.py --message "Where is my order A-1002?"
    python project/helpdesk_agent.py --message "I want a refund for order A-1001" --approve
    python project/helpdesk_agent.py          (interactive, asks you to approve refunds)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import ToolCall, get_llm  # noqa: E402
from project.agent import Agent, AgentResult  # noqa: E402
from project.mock_brain import scripted_brain  # noqa: E402
from project.tools import build_registry  # noqa: E402


def print_result(result: AgentResult) -> None:
    for number, step in enumerate(result.steps, start=1):
        approval = "" if step.approved is None else f" approved={step.approved}"
        print(f"  step {number}: {step.tool}({step.arguments}){approval}")
        print(f"          -> {step.result[:150]}")
    print(f"\nAgent: {result.answer}")
    print(f"[{result.stop_reason}, {len(result.steps)} tool calls, ~{result.tokens} tokens]")


def ask_human(call: ToolCall) -> bool:
    return input(f"\nAPPROVAL NEEDED: {call.name}({call.arguments}). Allow? [y/N] ").strip().lower() == "y"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message")
    parser.add_argument("--approve", action="store_true", help="Auto-approve actions (demo only)")
    args = parser.parse_args()

    approver = (lambda call: True) if args.approve else ask_human
    agent = Agent(get_llm(mock_handler=scripted_brain), build_registry(), approver=approver)

    if args.message:
        print_result(agent.run(args.message))
        return

    print("Acme Helpdesk. Try: 'Where is my order A-1002?' or 'Refund order A-1001'. Type 'exit' to quit.")
    while True:
        message = input("\nYou: ").strip()
        if message.lower() in {"exit", "quit"}:
            return
        if message:
            print_result(agent.run(message))


if __name__ == "__main__":
    main()
