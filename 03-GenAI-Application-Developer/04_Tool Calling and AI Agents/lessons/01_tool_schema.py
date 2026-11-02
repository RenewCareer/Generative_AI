"""Lesson 1: a tool is a function plus a description the model can read.

The model never runs anything. It only asks, and your code stays in control.

Run: python lessons/01_tool_schema.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.tools import build_registry  # noqa: E402


def main() -> None:
    registry = build_registry()
    print("What the model sees for one tool:")
    print(json.dumps(registry.schemas(["check_refund_eligibility"])[0], indent=2))

    print("\nAll tools:")
    for tool in registry.tools.values():
        flag = "  [needs human approval]" if tool.requires_approval else ""
        print(f"  - {tool.name}{flag}")

    print("\nWhat happens when arguments are good, bad, or the tool fails:")
    for name, arguments in [
        ("get_order", {"order_id": "A-1001"}),
        ("get_order", {"wrong_field": 1}),
        ("get_order", {"order_id": "Z-9999"}),
        ("delete_database", {}),
    ]:
        print(f"  {name}({arguments})\n    -> {registry.execute(name, arguments)[:130]}")
    print("\nErrors come back as data, so the model can read them and try something else.")


if __name__ == "__main__":
    main()
