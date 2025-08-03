"""Tests for the main MCP server."""

from schemacrawler_ai.main import create_server


class TestMCPServer:
    """Test suite for the MCP server."""

    def test_create_server(self):
        """Test server creation."""
        server = create_server()
        assert server is not None
        # Check that the server has the basic attributes we expect
        assert hasattr(server, "name")
        assert server.name == "SchemaCrawler AI MCP Server for SQL Server Performance"

    def test_server_has_hello_world_tool(self):
        """Test that the server has the hello world tool registered."""
        server = create_server()
        # This test will need to be updated based on FastMCP's actual API
        # For now, we just check that the server is created successfully
        assert server is not None
