"""Lesson 5: Model Context Protocol (MCP), a standard way to expose tools to any AI app.

Without MCP, each app writes a custom integration for each system. With MCP, a system exposes
one server, and any compatible client can discover and call its tools.

Run the demo : python lessons/05_mcp_server.py
Serve for real: python lessons/05_mcp_server.py --serve     (over stdio, for an MCP client)
"""

import asyncio
import sys
from pathlib import Path

from mcp import Client
from mcp.server.mcpserver import MCPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.tools import load_orders  # noqa: E402

server = MCPServer("acme-orders")
ORDERS = load_orders()


@server.tool()
def get_order_status(order_id: str) -> str:
    """Get the delivery status of an Acme order by its ID, such as A-1001."""
    order = ORDERS.get(order_id)
    return order["status"] if order else f"No order with ID {order_id}"


async def demo() -> None:
    # Connect in memory. A desktop app or IDE would connect over stdio or HTTP instead.
    async with Client(server) as client:
        tools = await client.list_tools()
        print("Tools the client discovered at runtime:")
        for tool in tools.tools:
            print(f"  - {tool.name}: {tool.description}")
        result = await client.call_tool("get_order_status", {"order_id": "A-1002"})
        print(f"\nget_order_status(A-1002) -> {result.content[0].text}")
    print("\nThe client knew nothing about this tool until it asked. That is the value of MCP.")
    print("Security still matters: only connect to servers you trust, and review their permissions.")


if __name__ == "__main__":
    if "--serve" in sys.argv:
        server.run()
    else:
        asyncio.run(demo())
