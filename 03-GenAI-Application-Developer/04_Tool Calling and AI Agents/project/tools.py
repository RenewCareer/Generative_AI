"""A tool registry: JSON schemas come from Python type hints, and arguments are validated."""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError, create_model

from genai_kit import COURSE_DATA, BM25Index, load_course_chunks


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]
    parameters: dict[str, Any]
    model: type
    requires_approval: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: dict[str, Tool] = {}

    def register(self, requires_approval: bool = False) -> Callable:
        """Decorator. The docstring tells the model when to use the tool, so write it well."""

        def decorator(function: Callable) -> Callable:
            fields = {}
            for name, parameter in inspect.signature(function).parameters.items():
                default = ... if parameter.default is inspect.Parameter.empty else parameter.default
                fields[name] = (parameter.annotation, default)
            model = create_model(f"{function.__name__}_args", **fields)
            schema = model.model_json_schema()
            schema.pop("title", None)
            self.tools[function.__name__] = Tool(
                name=function.__name__,
                description=inspect.getdoc(function) or "",
                function=function,
                parameters=schema,
                model=model,
                requires_approval=requires_approval,
            )
            return function

        return decorator

    def schemas(self, names: list[str] | None = None) -> list[dict[str, Any]]:
        selected = names or list(self.tools)
        return [
            {
                "name": self.tools[name].name,
                "description": self.tools[name].description,
                "parameters": self.tools[name].parameters,
            }
            for name in selected
        ]

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Run a tool. Failures become messages the model can read and react to."""
        tool = self.tools.get(name)
        if tool is None:
            return json.dumps({"error": f"Unknown tool {name!r}. Available: {sorted(self.tools)}"})
        try:
            validated = tool.model(**arguments).model_dump()
        except ValidationError as error:
            return json.dumps({"error": "Invalid arguments", "details": error.errors(include_url=False, include_context=False)}, default=str)
        try:
            return json.dumps(tool.function(**validated), default=str)
        except Exception as error:
            return json.dumps({"error": f"{type(error).__name__}: {error}"})


# ---------------------------------------------------------------- Helpdesk tools

REFUND_WINDOW_DAYS = 30


def load_orders() -> dict[str, dict]:
    orders = json.loads((COURSE_DATA / "orders.json").read_text(encoding="utf-8"))
    return {order["order_id"]: order for order in orders}


def build_registry(orders: dict[str, dict] | None = None) -> ToolRegistry:
    """Each registry gets its own data, so tests and sessions do not affect each other."""
    registry = ToolRegistry()
    orders = orders if orders is not None else load_orders()
    refunds: dict[str, float] = {}
    kb = BM25Index(chunk for chunk in load_course_chunks() if chunk.metadata["access"] == "public")

    @registry.register()
    def get_order(order_id: str) -> dict:
        """Look up an order's status, item, total and delivery age. Use it whenever a message mentions an order ID such as A-1001."""
        order = orders.get(order_id)
        if order is None:
            raise KeyError(f"No order with ID {order_id}")
        return {key: value for key, value in order.items() if key != "customer"}

    @registry.register()
    def check_refund_eligibility(order_id: str) -> dict:
        """Check whether an order can be refunded under the 30 day policy. Always use this before issue_refund."""
        order = orders.get(order_id)
        if order is None:
            raise KeyError(f"No order with ID {order_id}")
        if order_id in refunds:
            return {"eligible": False, "reason": "Already refunded"}
        if order["status"] != "delivered":
            return {"eligible": False, "reason": f"Order is {order['status']}, not delivered"}
        if order["delivered_days_ago"] > REFUND_WINDOW_DAYS:
            return {"eligible": False, "reason": f"Delivered {order['delivered_days_ago']} days ago, outside the {REFUND_WINDOW_DAYS} day window"}
        return {"eligible": True, "amount": order["total"]}

    @registry.register(requires_approval=True)
    def issue_refund(order_id: str, reason: str) -> dict:
        """Issue a full refund. This moves real money and needs human approval. Use only after check_refund_eligibility returns eligible."""
        # Tools enforce business rules themselves. Never rely on the model having obeyed.
        eligibility = check_refund_eligibility(order_id)
        if not eligibility["eligible"]:
            raise ValueError(f"Refund not allowed: {eligibility['reason']}")
        refunds[order_id] = eligibility["amount"]
        return {"refunded": eligibility["amount"], "order_id": order_id, "reason": reason}

    @registry.register()
    def search_policies(query: str, limit: int = 2) -> list[dict]:
        """Search public Acme policies on returns, shipping, warranty and products. Use it for general questions, not for a specific order."""
        return [{"source": hit.chunk.id, "text": hit.chunk.text} for hit in kb.search(query, k=limit)]

    @registry.register()
    def escalate_to_human(summary: str) -> dict:
        """Hand the conversation to a human agent. Use it for legal threats, anger, or anything the other tools cannot solve."""
        return {"ticket": "ESC-1042", "summary": summary, "status": "queued"}

    registry.refunds = refunds
    return registry
