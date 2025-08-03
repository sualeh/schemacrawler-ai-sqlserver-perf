"""Tests for the Hello World MCP tool."""

import pytest

from schemacrawler_ai.tools.hello_world import hello_world_tool


class TestHelloWorldTool:
    """Test suite for hello_world_tool."""

    @pytest.mark.asyncio
    async def test_hello_world_with_valid_name(self):
        """Test executing the tool with a valid name."""
        result = await hello_world_tool("Alice")

        assert isinstance(result, dict)
        assert "message" in result
        assert "Alice" in result["message"]
        assert "Hello, Alice!" in result["message"]
        assert result["tool"] == "hello_world"
        assert result["success"] is True
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_hello_world_with_different_names(self):
        """Test executing the tool with different names."""
        test_names = ["Bob", "Charlie", "Diana", "Eve"]

        for name in test_names:
            result = await hello_world_tool(name)

            assert name in result["message"]
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_hello_world_with_empty_name(self):
        """Test that empty name still works."""
        result = await hello_world_tool("")

        assert isinstance(result, dict)
        assert result["success"] is True
        assert "Hello, !" in result["message"]

    @pytest.mark.asyncio
    async def test_hello_world_return_structure(self):
        """Test that the return structure is correct."""
        result = await hello_world_tool("Test User")

        required_keys = ["message", "timestamp", "tool", "success"]
        for key in required_keys:
            assert key in result

        assert result["tool"] == "hello_world"
        assert isinstance(result["success"], bool)
        assert isinstance(result["message"], str)
        assert isinstance(result["timestamp"], str)
