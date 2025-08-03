"""Tests for the Hello World MCP tool."""

import pytest

from schemacrawler_ai.tools.version import version_tool


class TestVersionTool:
    """Test suite for version_tool."""

    @pytest.mark.asyncio
    async def test_version_with_empty_name(self):
        """Test that empty name still works."""
        result = await version_tool()

        assert isinstance(result, dict)
        assert result["success"] is True
        assert "SchemaCrawler" in result["message"]

    @pytest.mark.asyncio
    async def test_version_return_structure(self):
        """Test that the return structure is correct."""
        result = await version_tool()

        required_keys = ["message", "timestamp", "tool", "success"]
        for key in required_keys:
            assert key in result

        assert result["tool"] == "version"
        assert isinstance(result["success"], bool)
        assert isinstance(result["message"], str)
        assert isinstance(result["timestamp"], str)
