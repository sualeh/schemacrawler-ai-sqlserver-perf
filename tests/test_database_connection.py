"""Tests for database connection module."""

import os
from unittest.mock import patch, MagicMock, call
import pytest

from schemacrawler_ai_sqlserver_perf.database.config import DatabaseConfig
from schemacrawler_ai_sqlserver_perf.database.connection import (
    DatabaseConnection,
    create_connection,
    validate_database_connection,
)


class TestDatabaseConnection:
    """Test suite for DatabaseConnection."""

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

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_connect_success(self, mock_pyodbc, config):
        """Test successful database connection."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)
        connection = db_conn.connect()

        assert connection == mock_connection
        mock_pyodbc.connect.assert_called_once()
        connection_string = mock_pyodbc.connect.call_args[0][0]
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in connection_string
        assert "SERVER=localhost,1433" in connection_string

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_connect_failure(self, mock_pyodbc, config):
        """Test database connection failure."""
        mock_pyodbc.connect.side_effect = Exception("Connection failed")

        db_conn = DatabaseConnection(config)

        with pytest.raises(Exception, match="Connection failed"):
            db_conn.connect()

    def test_connect_without_pyodbc(self, config):
        """Test connection attempt without pyodbc installed."""
        with patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc", None):
            db_conn = DatabaseConnection(config)

            with pytest.raises(ImportError, match="pyodbc is required"):
                db_conn.connect()

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_disconnect(self, mock_pyodbc, config):
        """Test database disconnection."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)
        db_conn.connect()
        db_conn.disconnect()

        mock_connection.close.assert_called_once()
        assert db_conn._connection is None

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_disconnect_with_error(self, mock_pyodbc, config):
        """Test database disconnection with error."""
        mock_connection = MagicMock()
        mock_connection.close.side_effect = Exception("Close failed")
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)
        db_conn.connect()

        # Should not raise exception
        db_conn.disconnect()

        mock_connection.close.assert_called_once()
        assert db_conn._connection is None

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_validate_connection_success(self, mock_pyodbc, config):
        """Test successful connection validation."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value = mock_cursor
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)
        result = db_conn.validate_connection()

        assert result is True
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_validate_connection_failure(self, mock_pyodbc, config):
        """Test connection validation failure."""
        mock_pyodbc.connect.side_effect = Exception("Connection failed")

        db_conn = DatabaseConnection(config)
        result = db_conn.validate_connection()

        assert result is False

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_context_manager_get_connection(self, mock_pyodbc, config):
        """Test context manager for database connections."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)

        with db_conn.get_connection() as connection:
            assert connection == mock_connection

        mock_connection.close.assert_called_once()

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_context_manager_with_statement(self, mock_pyodbc, config):
        """Test using DatabaseConnection as context manager."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)

        with db_conn as connection:
            assert connection == mock_connection

        mock_connection.close.assert_called_once()

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.pyodbc")
    def test_context_manager_with_exception(self, mock_pyodbc, config):
        """Test context manager behavior with exception."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        db_conn = DatabaseConnection(config)

        try:
            with db_conn.get_connection() as connection:
                assert connection == mock_connection
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Connection should still be closed
        mock_connection.close.assert_called_once()


class TestConnectionFunctions:
    """Test suite for connection utility functions."""

    @patch(
        "schemacrawler_ai_sqlserver_perf.database.connection.DatabaseConfig.from_environment"
    )
    def test_create_connection_from_environment(self, mock_from_env):
        """Test creating connection from environment variables."""
        mock_config = MagicMock()
        mock_from_env.return_value = mock_config

        connection = create_connection()

        assert isinstance(connection, DatabaseConnection)
        assert connection.config == mock_config
        mock_from_env.assert_called_once()

    def test_create_connection_with_config(self):
        """Test creating connection with provided configuration."""
        config = DatabaseConfig(
            server="sqlserver",
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
        )

        connection = create_connection(config)

        assert isinstance(connection, DatabaseConnection)
        assert connection.config == config

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.create_connection")
    def test_validate_database_connection_success(self, mock_create_connection):
        """Test successful database connection validation."""
        mock_connection = MagicMock()
        mock_connection.validate_connection.return_value = True
        mock_create_connection.return_value = mock_connection

        result = validate_database_connection()

        assert result is True
        mock_create_connection.assert_called_once()
        mock_connection.validate_connection.assert_called_once()

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.create_connection")
    def test_validate_database_connection_failure(self, mock_create_connection):
        """Test database connection validation failure."""
        mock_connection = MagicMock()
        mock_connection.validate_connection.return_value = False
        mock_create_connection.return_value = mock_connection

        result = validate_database_connection()

        assert result is False

    @patch("schemacrawler_ai_sqlserver_perf.database.connection.create_connection")
    def test_validate_database_connection_exception(self, mock_create_connection):
        """Test database connection validation with exception."""
        mock_create_connection.side_effect = Exception("Configuration error")

        result = validate_database_connection()

        assert result is False


class TestIntegration:
    """Integration tests for database module."""

    def test_full_environment_configuration_flow(self):
        """Test complete flow from environment variables to connection."""
        env_vars = {
            "SCHCRWLR_JDBC_URL": "jdbc:sqlserver://localhost:1433;databaseName=testdb",
            "SCHCRWLR_DATABASE_USER": "testuser",
            "SCHCRWLR_DATABASE_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "schemacrawler_ai_sqlserver_perf.database.connection.pyodbc"
            ) as mock_pyodbc:
                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.fetchone.return_value = (1,)
                mock_connection.cursor.return_value = mock_cursor
                mock_pyodbc.connect.return_value = mock_connection

                # Test the complete flow
                result = validate_database_connection()

                assert result is True
                mock_pyodbc.connect.assert_called_once()

                # Verify connection string
                connection_string = mock_pyodbc.connect.call_args[0][0]
                assert "DRIVER={ODBC Driver 17 for SQL Server}" in connection_string
                assert "SERVER=localhost,1433" in connection_string
                assert "DATABASE=testdb" in connection_string
                assert "UID=testuser" in connection_string
                assert "PWD=testpass" in connection_string
