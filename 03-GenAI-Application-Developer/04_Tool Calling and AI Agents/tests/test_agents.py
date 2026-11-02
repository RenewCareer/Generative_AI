import asyncio
import json
from pathlib import Path

from mcp import Client

from genai_kit import LLMResponse, MockClient, ToolCall
from genai_kit.testing import load_lesson
from project.agent import Agent
from project.mock_brain import scripted_brain
from project.tools import build_registry

LESSONS = Path(__file__).resolve().parents[1] / "lessons"


def brain() -> MockClient:
    return MockClient(scripted_brain)


def test_schema_is_generated_from_type_hints():
    schema = build_registry().schemas(["search_policies"])[0]
    assert schema["parameters"]["properties"]["query"]["type"] == "string"
    assert schema["parameters"]["required"] == ["query"]
    assert "Search public" in schema["description"]


def test_execute_returns_errors_as_data():
    registry = build_registry()
    assert "Unknown tool" in registry.execute("nope", {})
    assert "Invalid arguments" in registry.execute("get_order", {"bad": 1})
    assert "No order" in registry.execute("get_order", {"order_id": "Z"})
    assert json.loads(registry.execute("get_order", {"order_id": "A-1001"}))["status"] == "delivered"


def test_tool_output_excludes_customer_personal_data():
    assert "customer" not in json.loads(build_registry().execute("get_order", {"order_id": "A-1001"}))


def test_agent_answers_order_question():
    result = Agent(brain(), build_registry()).run("Where is my order A-1002?")
    assert [step.tool for step in result.steps] == ["get_order"]
    assert "in_transit" in result.answer


def test_refund_requires_approval_by_default():
    registry = build_registry()
    result = Agent(brain(), registry).run("Refund order A-1001")
    assert registry.refunds == {}
    assert result.steps[-1].approved is False


def test_approved_refund_moves_money_once():
    registry = build_registry()
    Agent(brain(), registry, approver=lambda call: True).run("Refund order A-1001")
    assert registry.refunds == {"A-1001": 149.0}
    second = registry.execute("issue_refund", {"order_id": "A-1001", "reason": "again"})
    assert "Refund not allowed" in second and registry.refunds == {"A-1001": 149.0}


def test_ineligible_refund_explained_without_issue_call():
    result = Agent(brain(), build_registry()).run("Refund order A-1003")
    assert "outside the 30 day window" in result.answer
    assert "issue_refund" not in [step.tool for step in result.steps]


def test_tool_blocks_bad_refund_even_if_model_skips_the_check():
    registry = build_registry()
    calls = [ToolCall("c", "issue_refund", {"order_id": "A-1003", "reason": "x"})]

    def reckless(messages, system, tools):
        if any(message["role"] == "tool" for message in messages):
            return "done"
        return LLMResponse("", "m", "mock", tool_calls=calls)

    Agent(MockClient(reckless), registry, approver=lambda call: True).run("x")
    assert registry.refunds == {}


def test_step_limit_stops_a_stuck_model():
    def stuck(messages, system, tools):
        return LLMResponse("", "m", "mock", tool_calls=[ToolCall("c", "search_policies", {"query": "x"})])

    result = Agent(MockClient(stuck), build_registry(), max_steps=3).run("x")
    assert result.stop_reason == "max_steps_reached" and len(result.steps) == 3


def test_token_budget_stops_the_agent():
    def stuck(messages, system, tools):
        return LLMResponse("", "m", "mock", tool_calls=[ToolCall("c", "search_policies", {"query": "x"})])

    result = Agent(MockClient(stuck), build_registry(), max_tokens_total=1).run("x")
    assert result.stop_reason == "token_budget_exceeded"


def test_legal_threat_escalates():
    result = Agent(brain(), build_registry()).run("My lawyer will sue you")
    assert result.steps[0].tool == "escalate_to_human"


def test_least_privilege_limits_tools_offered():
    agent = Agent(brain(), build_registry(), tool_names=["get_order"])
    seen = []

    def spy(messages, system, tools):
        seen.extend(tool["name"] for tool in tools)
        return "ok"

    agent.llm = MockClient(spy)
    agent.run("hello")
    assert seen == ["get_order"]


def test_router_picks_specialist():
    router = load_lesson(LESSONS / "04_router_multi_agent.py")
    assert router.mock_route([{"content": "order A-1002?"}], None)["specialist"] == "orders"
    assert router.mock_route([{"content": "my lawyer"}], None)["specialist"] == "human"


def test_mcp_server_lists_and_calls_tools():
    lesson = load_lesson(LESSONS / "05_mcp_server.py")

    async def go():
        async with Client(lesson.server) as client:
            tools = await client.list_tools()
            result = await client.call_tool("get_order_status", {"order_id": "A-1002"})
            return [tool.name for tool in tools.tools], result.content[0].text

    names, status = asyncio.run(go())
    assert names == ["get_order_status"] and status == "in_transit"
