"""A scripted stand-in for a tool-calling model, so that the agent loop runs without a key.

A real model makes these decisions itself from the tool descriptions. This one follows fixed
rules. It is NOT intelligent: it exists so that the loop, guardrails and tracing can be
demonstrated and tested deterministically.
"""

from __future__ import annotations

import json
import re

from genai_kit import LLMResponse, ToolCall

_counter = 0


def _call(name: str, **arguments) -> LLMResponse:
    global _counter
    _counter += 1
    return LLMResponse("", "mock-1", "mock", tool_calls=[ToolCall(f"call_{_counter}", name, arguments)])


def _results(messages: list[dict]) -> dict[str, dict]:
    """The latest result of each tool used so far in this conversation."""
    found: dict[str, dict] = {}
    for message in messages:
        if message["role"] == "tool":
            found[message["name"]] = json.loads(message["content"])
    return found


def scripted_brain(messages, system, tools) -> str | LLMResponse:
    question = next(message["content"] for message in messages if message["role"] == "user")
    lower = question.lower()
    results = _results(messages)
    available = {tool["name"] for tool in tools or []}
    order = re.search(r"\bA-\d{4}\b", question)

    if any(word in lower for word in ("lawyer", "sue", "legal")):
        if "escalate_to_human" not in results and "escalate_to_human" in available:
            return _call("escalate_to_human", summary=question[:200])
        return "I have passed this to a human colleague, who will contact you shortly."

    if order:
        order_id = order.group()
        if "get_order" not in results and "get_order" in available:
            return _call("get_order", order_id=order_id)
        if "error" in results.get("get_order", {}):
            return f"I could not find order {order_id}. Please check the ID."

        if "refund" in lower or "money back" in lower:
            if "check_refund_eligibility" not in results:
                return _call("check_refund_eligibility", order_id=order_id)
            eligibility = results["check_refund_eligibility"]
            if not eligibility.get("eligible"):
                return f"Order {order_id} cannot be refunded: {eligibility.get('reason')}."
            if "issue_refund" not in results:
                return _call("issue_refund", order_id=order_id, reason="Customer request")
            refund = results["issue_refund"]
            if "error" in refund:
                return f"The refund for {order_id} was not completed: {refund['error']}"
            return f"Your refund of {refund['refunded']} dollars for {order_id} has been issued."

        details = results.get("get_order", {})
        return f"Order {order_id} ({details.get('item')}) is currently {details.get('status')}."

    if "search_policies" not in results and "search_policies" in available:
        return _call("search_policies", query=question)
    hits = results.get("search_policies") or []
    if hits:
        return f"From {hits[0]['source']}: {' '.join(hits[0]['text'].split())[:200]}"
    return "I could not find an answer to that. Could you give me more detail?"
