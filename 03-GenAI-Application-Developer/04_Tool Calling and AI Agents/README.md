# Module 04: Tool Calling and AI Agents

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3.5 hours | **Next:** [Module 05](../05_multimodal%20AI/README.md)

## Learning outcomes

By the end, students can:

- Define tools a model can use, and validate every call
- Write the agent loop by hand, with nothing hidden
- Add guardrails: approvals, limits, least privilege and audit trails
- Explain routing, when to go multi-agent, and what MCP provides

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides: the model asks, your code acts | `presentation.pptx` |
| 25 min | Tool schemas | `lessons/01_tool_schema.py`, `project/tools.py` |
| 30 min | The agent loop | `lessons/02_agent_loop.py` |
| 30 min | Guardrails | `lessons/03_guardrails.py` |
| 20 min | Routing | `lessons/04_router_multi_agent.py` |
| 20 min | MCP | `lessons/05_mcp_server.py` |
| 15 min | Example app | `project/helpdesk_agent.py` |
| 45 min | Lab | Below |

## Concepts

**Tool calling.** The model never runs anything. It replies with a tool name and arguments, your code
validates and runs it, and the result goes back as a message. All real power stays in your code,
which is where the controls belong.

**Tool descriptions are prompts.** The model chooses from the name and description alone, so they
should say when to use the tool. Try making one worse with a real model, and watch the behaviour change.

**The agent loop.** Call the model. If it asks for tools, run them, add the results, and go round
again. If not, that is the answer. About 30 lines, in lesson 2. Understand this before using a framework.

**Guardrails.** Assume that the model will sometimes be wrong:

| Guardrail | What it does |
|---|---|
| Least privilege | Offer only the tools this task needs |
| Validation | Schemas reject bad arguments before code runs |
| Human approval | Actions that move money need a person, and the default is no |
| Rules in code | `issue_refund` re-checks eligibility, even if the model skipped that step |
| Hard limits | Maximum steps and a token budget stop a stuck agent |

The key demonstration is in lesson 3: a reckless model skips the check and tries to refund an
ineligible order, with approval, and the tool still refuses.

**Errors as data.** A failed tool returns a readable message, so that the model can adapt.

**Tool output is untrusted.** A web page or email returned by a tool can contain injected instructions.

**Multi-agent.** Start with one agent. Split for clear reasons: too many tools, or different permissions.
Routing to specialists is the most common pattern, and each specialist holds only the tools it needs. Frameworks
such as LangGraph can help with complex flows, but many production agents are one simple loop.

**MCP (Model Context Protocol)** is a standard way to expose tools. A system runs one server, and any
compatible client can discover and call its tools. Connect only to servers you trust, since tool
descriptions are also text that a model reads.

## Run it

```powershell
python lessons/01_tool_schema.py
python lessons/02_agent_loop.py
python lessons/03_guardrails.py
python lessons/04_router_multi_agent.py
python lessons/05_mcp_server.py
python project/helpdesk_agent.py --message "Where is my order A-1002?"
python project/helpdesk_agent.py
python -m pytest tests
```

**Offline, `project/mock_brain.py` makes the decisions, following fixed rules.** It is not intelligent. It lets the
loop and guardrails run repeatably. With a key, the same loop uses a real model.

### What to expect

```
USER: Hi, can I get a refund for order A-1003?

Turn 1: the model asks for get_order({'order_id': 'A-1003'})
Turn 2: the model asks for check_refund_eligibility({'order_id': 'A-1003'})
Turn 3: the model replied with no tool calls, so the loop ends.

ASSISTANT: Order A-1003 cannot be refunded: Delivered 45 days ago, outside the 30 day window.
```

## Code walkthrough

| Part | Teaching point |
|---|---|
| `tools.ToolRegistry.register` | The JSON schema is generated from type hints |
| `tools.ToolRegistry.execute` | Every failure becomes readable data |
| `tools.get_order` | Removes the customer's name: expose the minimum |
| `tools.issue_refund` | The rule is enforced in code |
| `agent.deny_all` | The safe default for approvals |
| `agent.Agent.run` | The loop, with both limits |

**Version note.** The course uses `mcp` 2.x, where `FastMCP` became `MCPServer`. Older tutorials will not match it.
Pin versions, and read the docs for the version you have.

## Industry standards

- Human approval for anything hard to reverse
- Idempotent tools: a retried action must not refund twice
- An audit log: who asked, what ran, what came back, and who approved it
- Evaluate whole tasks, not just single replies
- Excessive Agency, in the OWASP Top 10 for LLM Applications

## Lab

1. Add a `change_shipping_address` tool that works only before an order ships, and needs approval.
2. Write a test proving it refuses a delivered order, even when approved.
3. Add a daily refund limit in code, and show the agent explaining the limit to the customer.

**Marking notes.** Task 1: use `requires_approval=True`, and a docstring that says when to use the tool. Task 2 must
call the tool, not rely on the model. Task 3: raise an error inside `issue_refund`, so it returns as data. In mock
mode, extend `mock_brain`. With a key, a real model should explain the limit without changes.

## Check for understanding

1. Who executes a tool? *Your code. The model only requests it.*
2. Why enforce rules in the tool as well as the prompt? *Models do not always follow instructions.*
3. An agent reads an email saying to forward invoices to an outside address. What stops it? *Limited tools, approval and output checks, not only the prompt.*
4. When should you split into several agents? *When tool lists or permissions make one agent unreliable or unsafe.*
