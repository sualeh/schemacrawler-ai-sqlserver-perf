"""Tests for column statistics tool using SQL executor."""

import pytest
from unittest.mock import patch

from schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool import (
    column_statistics_tool,
)


class TestColumnStatisticsToolWithSQLExecutor:
    """Test suite for column statistics tool using SQL executor."""

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool.execute_sql_template"
    )
    async def test_column_statistics_tool_success(self, mock_execute_sql_template):
        """Test successful column statistics tool execution."""
        # Mock successful SQL execution with sample column data
        mock_execute_sql_template.return_value = {
            "success": True,
            "data": [
                {
                    "database_name": "TestDB",
                    "schema_name": "dbo",
                    "table_name": "Users",
                    "COLUMN_NAME": "UserId",
                    "DATA_TYPE": "int",
                    "IS_NULLABLE": "NO",
                    "CHARACTER_MAXIMUM_LENGTH": None,
                    "NUMERIC_PRECISION": 10,
                    "NUMERIC_SCALE": 0,
                    "ORDINAL_POSITION": 1,
                    "total_count": 1000,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
                {
                    "database_name": "TestDB",
                    "schema_name": "dbo",
                    "table_name": "Users",
                    "COLUMN_NAME": "UserName",
                    "DATA_TYPE": "varchar",
                    "IS_NULLABLE": "YES",
                    "CHARACTER_MAXIMUM_LENGTH": 255,
                    "NUMERIC_PRECISION": None,
                    "NUMERIC_SCALE": None,
                    "ORDINAL_POSITION": 2,
                    "total_count": 1000,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
            ],
        }

        result = await column_statistics_tool("TestDB", "dbo", "Users")

        # Verify the result
        assert result["success"] is True
        assert (
            result["message"]
            == "Column statistics retrieved successfully for TestDB.dbo.Users"
        )
        assert result["database_name"] == "TestDB"
        assert result["schema_name"] == "dbo"
        assert result["table_name"] == "Users"
        assert result["column_count"] == 2

        # Check that we have the expected column data
        data = result["data"]
        assert len(data) == 2

        # Check first column (UserId)
        user_id_col = data[0]
        assert user_id_col["COLUMN_NAME"] == "UserId"
        assert user_id_col["DATA_TYPE"] == "int"
        assert user_id_col["IS_NULLABLE"] == "NO"
        assert user_id_col["total_count"] == 1000

        # Check second column (UserName)
        username_col = data[1]
        assert username_col["COLUMN_NAME"] == "UserName"
        assert username_col["DATA_TYPE"] == "varchar"
        assert username_col["IS_NULLABLE"] == "YES"
        assert username_col["CHARACTER_MAXIMUM_LENGTH"] == 255

        # Verify the SQL template was called with correct substitutions
        mock_execute_sql_template.assert_called_once()
        call_args = mock_execute_sql_template.call_args
        substitutions = call_args[0][1]
        assert substitutions["database_name"] == "TestDB"
        assert substitutions["schema_name"] == "dbo"
        assert substitutions["table_name"] == "Users"

        # Verify SQL template contains expected components
        sql_template = call_args[0][0]
        assert "INFORMATION_SCHEMA.COLUMNS" in sql_template
        assert "{{database_name}}" in sql_template
        assert "{{schema_name}}" in sql_template
        assert "{{table_name}}" in sql_template

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool.execute_sql_template"
    )
    async def test_column_statistics_tool_no_data(self, mock_execute_sql_template):
        """Test column statistics tool with no data returned (table not found)."""
        # Mock successful SQL execution but no data (table doesn't exist)
        mock_execute_sql_template.return_value = {"success": True, "data": []}

        result = await column_statistics_tool("TestDB", "dbo", "NonExistentTable")

        # Verify the result
        assert result["success"] is True
        assert (
            result["message"]
            == "Column statistics retrieved successfully for TestDB.dbo.NonExistentTable"
        )
        assert result["database_name"] == "TestDB"
        assert result["schema_name"] == "dbo"
        assert result["table_name"] == "NonExistentTable"
        assert result["column_count"] == 0
        assert result["data"] == []

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool.execute_sql_template"
    )
    async def test_column_statistics_tool_sql_failure(self, mock_execute_sql_template):
        """Test column statistics tool with SQL execution failure."""
        # Mock SQL execution failure
        mock_execute_sql_template.return_value = {
            "success": False,
            "data": [],
            "error": "Table access denied",
        }

        result = await column_statistics_tool("TestDB", "dbo", "SecureTable")

        # Verify the result
        assert result["success"] is False
        assert (
            "Failed to retrieve column statistics for TestDB.dbo.SecureTable: Table access denied"
            in result["message"]
        )
        assert result["database_name"] == "TestDB"
        assert result["schema_name"] == "dbo"
        assert result["table_name"] == "SecureTable"
        assert result["column_count"] == 0
        assert result["error"] == "Table access denied"
        assert result["data"] == []

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool.execute_sql_template"
    )
    async def test_column_statistics_tool_exception(self, mock_execute_sql_template):
        """Test column statistics tool with unexpected exception."""
        # Mock unexpected exception
        mock_execute_sql_template.side_effect = Exception("Database connection lost")

        result = await column_statistics_tool("TestDB", "dbo", "Users")

        # Verify the result
        assert result["success"] is False
        assert (
            "Column statistics tool failed: Database connection lost"
            in result["message"]
        )
        assert result["database_name"] == "TestDB"
        assert result["schema_name"] == "dbo"
        assert result["table_name"] == "Users"
        assert result["column_count"] == 0
        assert result["error"] == "Database connection lost"
        assert result["data"] == []

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool.execute_sql_template"
    )
    async def test_column_statistics_tool_with_complex_names(
        self, mock_execute_sql_template
    ):
        """Test column statistics tool with special characters in names."""
        # Mock successful SQL execution with special characters in names
        mock_execute_sql_template.return_value = {
            "success": True,
            "data": [
                {
                    "database_name": "Test-DB_2023",
                    "schema_name": "custom_schema",
                    "table_name": "User Data",
                    "COLUMN_NAME": "User ID",
                    "DATA_TYPE": "uniqueidentifier",
                    "IS_NULLABLE": "NO",
                    "CHARACTER_MAXIMUM_LENGTH": None,
                    "NUMERIC_PRECISION": None,
                    "NUMERIC_SCALE": None,
                    "ORDINAL_POSITION": 1,
                    "total_count": 500,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
            ],
        }

        result = await column_statistics_tool(
            "Test-DB_2023", "custom_schema", "User Data"
        )

        # Verify the result handles special characters properly
        assert result["success"] is True
        assert result["database_name"] == "Test-DB_2023"
        assert result["schema_name"] == "custom_schema"
        assert result["table_name"] == "User Data"
        assert result["column_count"] == 1

        # Verify substitutions were passed correctly
        mock_execute_sql_template.assert_called_once()
        call_args = mock_execute_sql_template.call_args
        substitutions = call_args[0][1]
        assert substitutions["database_name"] == "Test-DB_2023"
        assert substitutions["schema_name"] == "custom_schema"
        assert substitutions["table_name"] == "User Data"

    @pytest.mark.asyncio
    @patch(
        "schemacrawler_ai_sqlserver_perf.tools.column_statistics_tool.execute_sql_template"
    )
    async def test_column_statistics_tool_multiple_data_types(
        self, mock_execute_sql_template
    ):
        """Test column statistics tool with various SQL Server data types."""
        # Mock successful SQL execution with various data types
        mock_execute_sql_template.return_value = {
            "success": True,
            "data": [
                {
                    "database_name": "TestDB",
                    "schema_name": "dbo",
                    "table_name": "DataTypes",
                    "COLUMN_NAME": "Id",
                    "DATA_TYPE": "int",
                    "IS_NULLABLE": "NO",
                    "CHARACTER_MAXIMUM_LENGTH": None,
                    "NUMERIC_PRECISION": 10,
                    "NUMERIC_SCALE": 0,
                    "ORDINAL_POSITION": 1,
                    "total_count": 100,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
                {
                    "database_name": "TestDB",
                    "schema_name": "dbo",
                    "table_name": "DataTypes",
                    "COLUMN_NAME": "Name",
                    "DATA_TYPE": "nvarchar",
                    "IS_NULLABLE": "YES",
                    "CHARACTER_MAXIMUM_LENGTH": 100,
                    "NUMERIC_PRECISION": None,
                    "NUMERIC_SCALE": None,
                    "ORDINAL_POSITION": 2,
                    "total_count": 100,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
                {
                    "database_name": "TestDB",
                    "schema_name": "dbo",
                    "table_name": "DataTypes",
                    "COLUMN_NAME": "Price",
                    "DATA_TYPE": "decimal",
                    "IS_NULLABLE": "YES",
                    "CHARACTER_MAXIMUM_LENGTH": None,
                    "NUMERIC_PRECISION": 18,
                    "NUMERIC_SCALE": 2,
                    "ORDINAL_POSITION": 3,
                    "total_count": 100,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
                {
                    "database_name": "TestDB",
                    "schema_name": "dbo",
                    "table_name": "DataTypes",
                    "COLUMN_NAME": "CreatedDate",
                    "DATA_TYPE": "datetime2",
                    "IS_NULLABLE": "NO",
                    "CHARACTER_MAXIMUM_LENGTH": None,
                    "NUMERIC_PRECISION": None,
                    "NUMERIC_SCALE": None,
                    "ORDINAL_POSITION": 4,
                    "total_count": 100,
                    "min_value": None,
                    "max_value": None,
                    "null_count": None,
                    "distinct_count": None,
                },
            ],
        }

        result = await column_statistics_tool("TestDB", "dbo", "DataTypes")

        # Verify the result handles multiple data types
        assert result["success"] is True
        assert result["column_count"] == 4

        data = result["data"]
        
        # Check each data type is represented correctly
        data_types = [col["DATA_TYPE"] for col in data]
        assert "int" in data_types
        assert "nvarchar" in data_types
        assert "decimal" in data_types
        assert "datetime2" in data_types

        # Verify nullable and non-nullable columns
        nullable_cols = [col for col in data if col["IS_NULLABLE"] == "YES"]
        non_nullable_cols = [col for col in data if col["IS_NULLABLE"] == "NO"]
        assert len(nullable_cols) == 2  # Name and Price
        assert len(non_nullable_cols) == 2  # Id and CreatedDate