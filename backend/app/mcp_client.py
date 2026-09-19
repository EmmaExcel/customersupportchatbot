import json
from contextlib import asynccontextmanager

from mcp.client.session import ClientSession
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

from shared.config import get

MCP_URL = get("MCP_URL", "http://127.0.0.1:8001/mcp")


@asynccontextmanager
async def mcp_session():
    async with create_mcp_http_client() as http_client:
        async with streamable_http_client(MCP_URL, http_client=http_client) as streams:
            read_stream, write_stream, _ = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session


async def call_tools(session, tool_calls):
    results = []
    for call in tool_calls:
        name = call.function.name
        try:
            arguments = json.loads(call.function.arguments or "{}")
        except json.JSONDecodeError:
            arguments = {}
        result = await session.call_tool(name, arguments)
        parts = []
        for block in result.content:
            text = getattr(block, "text", "")
            if text:
                parts.append(text)
        results.append({"id": call.id, "content": "\n".join(parts) if parts else "{}"})
    return results
