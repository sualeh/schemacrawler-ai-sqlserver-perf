"""Tests for database connection tool using SQL executor."""

import pytest
from unittest.mock import patch

from schemacrawler_ai_sqlserver_perf.tools.database_connection_tool import (
    database_connection_tool,
)


class TestDatabaseConnectionToolWithSQLExecutor:
    """Test suite for database connection tool using SQL executor."""

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.execute_sql_template"
    )
    async def test_database_connection_tool_success(self, mock_execute_sql_template):
        """Test successful database connection tool execution."""
        # Mock successful SQL execution
        mock_execute_sql_template.return_value = {
            "success": True,
            "data": [
                {
                    "version": "Microsoft SQL Server 2019 (RTM) - 15.0.2000.5 (X64)\n\tSep 24 2019 13:48:23",
                    "product_name": "Microsoft SQL Server",
                    "product_version": "15.0.2000.5",
                }
            ],
        }

        result = await database_connection_tool()

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Database connection successful"
        assert result["connection_status"] == "connected"
        assert result["tool"] == "database_connection"

        # Check database info
        db_info = result["database_info"]
        assert db_info["product_name"] == "Microsoft SQL Server"
        assert db_info["product_version"] == "15.0.2000.5"
        assert (
            db_info["version_string"]
            == "Microsoft SQL Server 2019 (RTM) - 15.0.2000.5 (X64)"
        )
        assert "Microsoft SQL Server 2019" in db_info["full_version"]

        # Verify timestamp is present
        assert "timestamp" in result

        # Verify the SQL template was called
        mock_execute_sql_template.assert_called_once()
        call_args = mock_execute_sql_template.call_args
        sql_template = call_args[0][0]
        assert "@@VERSION" in sql_template
        assert "SERVERPROPERTY('ProductName')" in sql_template
        assert "SERVERPROPERTY('ProductVersion')" in sql_template

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.execute_sql_template"
    )
    async def test_database_connection_tool_no_data(self, mock_execute_sql_template):
        """Test database connection tool with no data returned."""
        # Mock successful SQL execution but no data
        mock_execute_sql_template.return_value = {"success": True, "data": []}

        result = await database_connection_tool()

        # Verify the result
        assert result["success"] is True
        assert (
            result["message"]
            == "Database connection successful but no version information available"
        )
        assert result["connection_status"] == "connected"

        # Check database info defaults
        db_info = result["database_info"]
        assert db_info["product_name"] == "Unknown"
        assert db_info["product_version"] == "Unknown"
        assert db_info["version_string"] == "Unknown"

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.execute_sql_template"
    )
    async def test_database_connection_tool_sql_failure(
        self, mock_execute_sql_template
    ):
        """Test database connection tool with SQL execution failure."""
        # Mock SQL execution failure
        mock_execute_sql_template.return_value = {
            "success": False,
            "data": [],
            "error": "Connection timeout",
        }

        result = await database_connection_tool()

        # Verify the result
        assert result["success"] is False
        assert "Database connection failed: Connection timeout" in result["message"]
        assert result["connection_status"] == "failed"
        assert result["error"] == "Connection timeout"
        assert result["database_info"] is None

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.execute_sql_template"
    )
    async def test_database_connection_tool_exception(self, mock_execute_sql_template):
        """Test database connection tool with unexpected exception."""
        # Mock unexpected exception
        mock_execute_sql_template.side_effect = Exception("Unexpected error")

        result = await database_connection_tool()

        # Verify the result
        assert result["success"] is False
        assert "Database connection tool failed: Unexpected error" in result["message"]
        assert result["connection_status"] == "failed"
        assert result["error"] == "Unexpected error"
        assert result["database_info"] is None

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.database_connection_tool.execute_sql_template"
    )
    async def test_database_connection_tool_null_values(
        self, mock_execute_sql_template
    ):
        """Test database connection tool with null/empty values in response."""
        # Mock SQL execution with null/empty values
        mock_execute_sql_template.return_value = {
            "success": True,
            "data": [{"version": None, "product_name": "", "product_version": None}],
        }

        result = await database_connection_tool()

        # Verify the result handles null/empty values gracefully
        assert result["success"] is True

        db_info = result["database_info"]
        assert db_info["product_name"] == "Unknown"
        assert db_info["product_version"] == "Unknown"
        assert db_info["version_string"] == "Unknown"
        assert db_info["full_version"] == "Unknown"
