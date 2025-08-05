"""Tests for the Database Connection MCP tool."""

import pytest
from unittest.mock import patch, MagicMock

from schemacrawler_ai_sqlserver_perf.tools.database_connection_tool import database_connection_tool


class TestDatabaseConnectionTool:
    """Test suite for database_connection_tool."""

    @pytest.mark.asyncio
    async def test_database_connection_success(self):
        """Test successful database connection."""
        # Mock the database connection and query results
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_result = MagicMock()
        
        # Setup mock result values
        mock_result.version = "Microsoft SQL Server 2022 (RTM) - 16.0.1000.6 (X64) \nDeveloper Edition (64-bit)"
        mock_result.product_name = "Microsoft SQL Server"
        mock_result.product_version = "16.0.1000.6"
        
        mock_cursor.fetchone.return_value = mock_result
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock the create_connection function
        with patch('schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.create_connection') as mock_create_conn:
            mock_db_conn = MagicMock()
            mock_db_conn.get_connection.return_value.__enter__.return_value = mock_connection
            mock_create_conn.return_value = mock_db_conn
            
            result = await database_connection_tool()
            
            assert isinstance(result, dict)
            assert result["success"] is True
            assert result["tool"] == "database_connection"
            assert result["connection_status"] == "connected"
            assert "database_info" in result
            assert result["database_info"]["product_name"] == "Microsoft SQL Server"
            assert result["database_info"]["product_version"] == "16.0.1000.6"
            assert "Microsoft SQL Server 2022" in result["database_info"]["version_string"]

    @pytest.mark.asyncio
    async def test_database_connection_failure(self):
        """Test database connection failure."""
        # Mock the create_connection function to raise an exception
        with patch('schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.create_connection') as mock_create_conn:
            mock_create_conn.side_effect = ValueError("Database credentials are required")
            
            result = await database_connection_tool()
            
            assert isinstance(result, dict)
            assert result["success"] is False
            assert result["tool"] == "database_connection"
            assert result["connection_status"] == "failed"
            assert "Database credentials are required" in result["message"]
            assert result["database_info"] is None

    @pytest.mark.asyncio
    async def test_database_connection_no_version_info(self):
        """Test database connection with no version information."""
        # Mock the database connection and query results
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Mock fetchone to return None (no results)
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock the create_connection function
        with patch('schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.create_connection') as mock_create_conn:
            mock_db_conn = MagicMock()
            mock_db_conn.get_connection.return_value.__enter__.return_value = mock_connection
            mock_create_conn.return_value = mock_db_conn
            
            result = await database_connection_tool()
            
            assert isinstance(result, dict)
            assert result["success"] is True
            assert result["tool"] == "database_connection"
            assert result["connection_status"] == "connected"
            assert "no version information available" in result["message"]
            assert result["database_info"]["product_name"] == "Unknown"

    @pytest.mark.asyncio
    async def test_database_connection_return_structure(self):
        """Test that the return structure is correct."""
        # Mock a connection failure to test error structure
        with patch('schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.create_connection') as mock_create_conn:
            mock_create_conn.side_effect = Exception("Test error")
            
            result = await database_connection_tool()
            
            required_keys = ["message", "database_info", "connection_status", "timestamp", "tool", "success", "error"]
            for key in required_keys:
                assert key in result
            
            assert result["tool"] == "database_connection"
            assert isinstance(result["success"], bool)
            assert isinstance(result["message"], str)
            assert isinstance(result["timestamp"], str)
            assert result["connection_status"] in ["connected", "failed"]