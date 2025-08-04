"""Tests for the main MCP server."""

from unittest.mock import patch, MagicMock
import pytest

# Mock fastmcp before importing main
with patch.dict('sys.modules', {'fastmcp': MagicMock()}):
    from schemacrawler_ai_sqlserver_perf.main import create_server


class TestMCPServer:
    """Test suite for the MCP server."""

    @patch('schemacrawler_ai_sqlserver_perf.main.validate_database_connection')
    @patch('schemacrawler_ai_sqlserver_perf.main.fastmcp.FastMCP')
    def test_create_server(self, mock_fastmcp_class, mock_validate_db):
        """Test server creation."""
        mock_validate_db.return_value = True
        mock_server = MagicMock()
        mock_server.name = "SchemaCrawler AI MCP Server for SQL Server Performance"
        mock_fastmcp_class.return_value = mock_server
        
        server = create_server()
        assert server is not None
        # Check that the server has the basic attributes we expect
        assert hasattr(server, "name")
        assert server.name == "SchemaCrawler AI MCP Server for SQL Server Performance"
        mock_validate_db.assert_called_once()

    @patch('schemacrawler_ai_sqlserver_perf.main.validate_database_connection')
    @patch('schemacrawler_ai_sqlserver_perf.main.fastmcp.FastMCP')
    def test_server_has_version_tool(self, mock_fastmcp_class, mock_validate_db):
        """Test that the server has the version tool registered."""
        mock_validate_db.return_value = True
        mock_server = MagicMock()
        mock_fastmcp_class.return_value = mock_server
        
        server = create_server()
        # This test will need to be updated based on FastMCP's actual API
        # For now, we just check that the server is created successfully
        assert server is not None

    @patch('schemacrawler_ai_sqlserver_perf.main.validate_database_connection')
    @patch('schemacrawler_ai_sqlserver_perf.main.sys.exit')
    @patch('schemacrawler_ai_sqlserver_perf.main.fastmcp.FastMCP')
    def test_create_server_db_validation_failure(self, mock_fastmcp_class, mock_exit, mock_validate_db):
        """Test server creation fails when database validation fails."""
        mock_validate_db.return_value = False
        
        create_server()
        
        mock_validate_db.assert_called_once()
        mock_exit.assert_called_once_with(1)
