"""Tests for SQL executor module."""

import datetime
from unittest.mock import MagicMock, patch, call
import pytest

from schemacrawler_ai_sqlserver_perf.database.config import DatabaseConfig
from schemacrawler_ai_sqlserver_perf.database.sql_executor import (
    SQLExecutor,
    execute_sql_template,
    SQLTemplateError,
    SQLExecutionError,
)


class TestSQLExecutor:
    """Test suite for SQLExecutor."""

    @pytest.fixture
    def config(self):
        """Create a test database configuration."""
        return DatabaseConfig(
            server="sqlserver",
            host="localhost",
            port=1433,
            database="testdb",
            username="testuser",
            password="testpass",
        )

    @pytest.fixture
    def executor(self, config):
        """Create a SQLExecutor instance."""
        return SQLExecutor(config)

    def test_substitute_template_simple(self, executor):
        """Test simple template substitution."""
        template = "SELECT * FROM {{table_name}} WHERE id = {{id}}"
        substitutions = {"table_name": "users", "id": "123"}

        result = executor.substitute_template(template, substitutions)

        assert result == "SELECT * FROM users WHERE id = 123"

    def test_substitute_template_string_escaping(self, executor):
        """Test that string values with single quotes are properly escaped."""
        template = "SELECT * FROM users WHERE name = '{{name}}'"
        substitutions = {"name": "O'Connor"}

        result = executor.substitute_template(template, substitutions)

        assert result == "SELECT * FROM users WHERE name = 'O''Connor'"

    def test_substitute_template_multiple_same_variable(self, executor):
        """Test template with same variable used multiple times."""
        template = (
            "SELECT {{field}}, {{field}}_backup FROM table WHERE {{field}} IS NOT NULL"
        )
        substitutions = {"field": "email"}

        result = executor.substitute_template(template, substitutions)

        assert result == "SELECT email, email_backup FROM table WHERE email IS NOT NULL"

    def test_substitute_template_missing_variables(self, executor):
        """Test template substitution with missing variables."""
        template = "SELECT * FROM {{table_name}} WHERE id = {{id}}"
        substitutions = {"table_name": "users"}  # Missing 'id'

        with pytest.raises(SQLTemplateError) as exc_info:
            executor.substitute_template(template, substitutions)

        assert "Missing substitution variables: {'id'}" in str(exc_info.value)

    def test_substitute_template_no_variables(self, executor):
        """Test template with no variables."""
        template = "SELECT COUNT(*) FROM users"
        substitutions = {}

        result = executor.substitute_template(template, substitutions)

        assert result == template

    def test_substitute_template_extra_variables(self, executor):
        """Test template substitution with extra variables (should be ignored)."""
        template = "SELECT * FROM {{table_name}}"
        substitutions = {"table_name": "users", "extra_var": "ignored"}

        result = executor.substitute_template(template, substitutions)

        assert result == "SELECT * FROM users"

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.create_connection")
    def test_execute_sql_success(self, mock_create_connection, executor):
        """Test successful SQL execution."""
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection = MagicMock()

        mock_create_connection.return_value = mock_db_connection
        mock_db_connection.get_connection.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection.cursor.return_value = mock_cursor

        # Mock cursor description and results
        mock_cursor.description = [
            ("id", None, None, None, None, None, None),
            ("name", None, None, None, None, None, None),
            ("created_date", None, None, None, None, None, None),
        ]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe", datetime.datetime(2023, 1, 1, 12, 0, 0)),
            (2, "Jane Smith", datetime.datetime(2023, 1, 2, 13, 30, 0)),
        ]

        sql = "SELECT id, name, created_date FROM users"
        result = executor.execute_sql(sql)

        # Verify the result
        expected = [
            {"id": 1, "name": "John Doe", "created_date": "2023-01-01T12:00:00"},
            {"id": 2, "name": "Jane Smith", "created_date": "2023-01-02T13:30:00"},
        ]
        assert result == expected

        # Verify database interactions
        mock_create_connection.assert_called_once_with(executor.config)
        mock_cursor.execute.assert_called_once_with(sql)
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.create_connection")
    def test_execute_sql_no_results(self, mock_create_connection, executor):
        """Test SQL execution with no results."""
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection = MagicMock()

        mock_create_connection.return_value = mock_db_connection
        mock_db_connection.get_connection.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection.cursor.return_value = mock_cursor

        # Mock empty results
        mock_cursor.description = [("count", None, None, None, None, None, None)]
        mock_cursor.fetchall.return_value = []

        sql = "SELECT COUNT(*) as count FROM users WHERE id = -1"
        result = executor.execute_sql(sql)

        assert result == []

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.create_connection")
    def test_execute_sql_null_values(self, mock_create_connection, executor):
        """Test SQL execution with NULL values."""
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection = MagicMock()

        mock_create_connection.return_value = mock_db_connection
        mock_db_connection.get_connection.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection.cursor.return_value = mock_cursor

        # Mock results with NULL values
        mock_cursor.description = [
            ("id", None, None, None, None, None, None),
            ("name", None, None, None, None, None, None),
        ]
        mock_cursor.fetchall.return_value = [(1, None), (2, "Jane")]

        result = executor.execute_sql("SELECT id, name FROM users")

        expected = [{"id": 1, "name": None}, {"id": 2, "name": "Jane"}]
        assert result == expected

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.create_connection")
    def test_execute_sql_connection_error(self, mock_create_connection, executor):
        """Test SQL execution with connection error."""
        mock_create_connection.side_effect = Exception("Connection failed")

        with pytest.raises(SQLExecutionError) as exc_info:
            executor.execute_sql("SELECT 1")

        assert "SQL execution failed: Connection failed" in str(exc_info.value)

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.create_connection")
    def test_execute_template_success(self, mock_create_connection, executor):
        """Test successful template execution."""
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection = MagicMock()

        mock_create_connection.return_value = mock_db_connection
        mock_db_connection.get_connection.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection.cursor.return_value = mock_cursor

        # Mock results
        mock_cursor.description = [("count", None, None, None, None, None, None)]
        mock_cursor.fetchall.return_value = [(5,)]

        template = "SELECT COUNT(*) as count FROM {{table_name}}"
        substitutions = {"table_name": "users"}

        result = executor.execute_template(template, substitutions)

        assert result["success"] is True
        assert result["data"] == [{"count": 5}]
        assert result["row_count"] == 1
        assert result["executed_sql"] == "SELECT COUNT(*) as count FROM users"
        assert result["template"] == template
        assert result["substitutions"] == substitutions
        assert result["error"] is None
        assert "timestamp" in result

    def test_execute_template_template_error(self, executor):
        """Test template execution with template error."""
        template = "SELECT * FROM {{table_name}} WHERE id = {{id}}"
        substitutions = {"table_name": "users"}  # Missing 'id'

        result = executor.execute_template(template, substitutions)

        assert result["success"] is False
        assert result["data"] == []
        assert result["row_count"] == 0
        assert result["executed_sql"] is None
        assert result["template"] == template
        assert result["substitutions"] == substitutions
        assert "Missing substitution variables" in result["error"]

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.create_connection")
    def test_execute_template_sql_error(self, mock_create_connection, executor):
        """Test template execution with SQL execution error."""
        mock_create_connection.side_effect = Exception("SQL error")

        template = "SELECT * FROM {{table_name}}"
        substitutions = {"table_name": "users"}

        result = executor.execute_template(template, substitutions)

        assert result["success"] is False
        assert result["data"] == []
        assert result["row_count"] == 0
        assert result["executed_sql"] is None
        assert result["template"] == template
        assert result["substitutions"] == substitutions
        assert "SQL execution failed" in result["error"]

    def test_execute_template_no_substitutions(self, executor):
        """Test template execution with no substitutions."""
        with patch.object(executor, "execute_sql") as mock_execute:
            mock_execute.return_value = [{"result": "test"}]

            template = "SELECT 'test' as result"
            result = executor.execute_template(template)

            assert result["success"] is True
            assert result["substitutions"] == {}


class TestConvenienceFunction:
    """Test the convenience function."""

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.SQLExecutor")
    def test_execute_sql_template_function(self, mock_sql_executor_class):
        """Test the execute_sql_template convenience function."""
        # Mock the SQLExecutor instance and its execute_template method
        mock_executor = MagicMock()
        mock_sql_executor_class.return_value = mock_executor
        mock_executor.execute_template.return_value = {"success": True, "data": []}

        template = "SELECT * FROM {{table_name}}"
        substitutions = {"table_name": "users"}
        config = DatabaseConfig(
            server="sqlserver",
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
        )

        result = execute_sql_template(template, substitutions, config)

        # Verify SQLExecutor was created with the right config
        mock_sql_executor_class.assert_called_once_with(config)

        # Verify execute_template was called with the right parameters
        mock_executor.execute_template.assert_called_once_with(template, substitutions)

        # Verify the result is passed through
        assert result == {"success": True, "data": []}

    @patch("schemacrawler_ai_sqlserver_perf.database.sql_executor.SQLExecutor")
    def test_execute_sql_template_function_defaults(self, mock_sql_executor_class):
        """Test the execute_sql_template function with default parameters."""
        mock_executor = MagicMock()
        mock_sql_executor_class.return_value = mock_executor
        mock_executor.execute_template.return_value = {"success": True}

        template = "SELECT 1"
        result = execute_sql_template(template)

        # Verify SQLExecutor was created with None config (should use environment)
        mock_sql_executor_class.assert_called_once_with(None)

        # Verify execute_template was called with None substitutions
        mock_executor.execute_template.assert_called_once_with(template, None)
