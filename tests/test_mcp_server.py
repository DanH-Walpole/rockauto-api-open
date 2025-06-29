import asyncio
import json
import pytest
from fastmcp import Client

from mcp_server import server


@pytest.mark.asyncio
async def test_tool_list_excludes_root():
    async with Client(server) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        assert "root" not in tool_names
        assert "get_makes_makes_get" in tool_names


@pytest.mark.asyncio
async def test_get_makes_via_client():
    async with Client(server) as client:
        result = await client.call_tool("get_makes_makes_get", {})
        data = json.loads(result[0].text)
        assert isinstance(data, list)
        assert len(data) > 50
