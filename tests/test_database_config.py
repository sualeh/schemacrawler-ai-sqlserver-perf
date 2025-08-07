"""Tests for database configuration module."""

import os
import pytest
from unittest.mock import patch

from schemacrawler_ai_sqlserver_perf.database.config import DatabaseConfig


class TestDatabaseConfig:
    """Test suite for DatabaseConfig."""

    def test_from_environment_with_connection_url(self):
        """Test configuration creation from connection URL."""
        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=testdb;"
            "UID=testuser;"
            "PWD=testpass"
        )
        env_vars = {
            "SCHCRWLR_CONNECTION_URL": connection_string,
            "SCHCRWLR_DATABASE_USER": "testuser",
            "SCHCRWLR_DATABASE_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig.from_environment()

            assert config.connection_url == connection_string
            assert config.server is None
            assert config.host is None
            assert config.port is None
            assert config.database is None
            assert config.username == "testuser"
            assert config.password == "testpass"

    def test_from_environment_with_individual_params(self):
        """Test configuration creation from individual parameters."""
        env_vars = {
            "SCHCRWLR_SERVER": "sqlserver",
            "SCHCRWLR_HOST": "localhost",
            "SCHCRWLR_PORT": "1433",
            "SCHCRWLR_DATABASE": "testdb",
            "SCHCRWLR_DATABASE_USER": "testuser",
            "SCHCRWLR_DATABASE_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig.from_environment()

            assert config.server == "sqlserver"
            assert config.host == "localhost"
            assert config.port == 1433
            assert config.database == "testdb"
            assert config.username == "testuser"
            assert config.password == "testpass"
            assert config.connection_url is None

    def test_from_environment_without_port(self):
        """Test configuration creation without port specification."""
        env_vars = {
            "SCHCRWLR_SERVER": "sqlserver",
            "SCHCRWLR_HOST": "localhost",
            "SCHCRWLR_DATABASE": "testdb",
            "SCHCRWLR_DATABASE_USER": "testuser",
            "SCHCRWLR_DATABASE_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig.from_environment()

            assert config.port is None

    def test_from_environment_missing_credentials(self):
        """Test that missing credentials raise an error."""
        env_vars = {
            "SCHCRWLR_SERVER": "sqlserver",
            "SCHCRWLR_HOST": "localhost",
            "SCHCRWLR_DATABASE": "testdb",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="Database credentials are required"):
                DatabaseConfig.from_environment()

    def test_from_environment_missing_connection_params(self):
        """Test that missing connection parameters raise an error."""
        env_vars = {
            "SCHCRWLR_HOST": "localhost",
            "SCHCRWLR_DATABASE_USER": "testuser",
            "SCHCRWLR_DATABASE_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(
                ValueError,
                match="Either SCHCRWLR_CONNECTION_URL or all of the following "
                      "are required",
            ):
                DatabaseConfig.from_environment()

    def test_validate_server_sqlserver(self):
        """Test server validation for SQL Server."""
        config = DatabaseConfig(
            server="sqlserver",
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
        )
        assert config.server == "sqlserver"

    def test_validate_server_uppercase(self):
        """Test server validation with uppercase."""
        config = DatabaseConfig(
            server="SQLSERVER",
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
        )
        assert config.server == "sqlserver"

    def test_validate_server_unsupported(self):
        """Test server validation with unsupported type."""
        with pytest.raises(ValueError, match="Unsupported server type"):
            DatabaseConfig(
                server="oracle",
                host="localhost",
                database="testdb",
                username="user",
                password="pass",
            )

    def test_get_connection_string_sqlserver(self):
        """Test SQL Server connection string generation."""
        config = DatabaseConfig(
            server="sqlserver",
            host="localhost",
            port=1433,
            database="testdb",
            username="testuser",
            password="testpass",
        )

        connection_string = config.get_connection_string()

        expected_parts = [
            "DRIVER={ODBC Driver 18 for SQL Server}",
            "SERVER=localhost,1433",
            "DATABASE=testdb",
            "UID=testuser",
            "PWD=testpass",
            "Encrypt=yes",
            "TrustServerCertificate=yes",
        ]

        for part in expected_parts:
            assert part in connection_string

    def test_get_connection_string_with_connection_url(self):
        """Test connection string generation with connection URL."""
        connection_url = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=testdb;"
            "UID=testuser;"
            "PWD=testpass"
        )
        config = DatabaseConfig(
            connection_url=connection_url,
            username="testuser",
            password="testpass",
        )

        connection_string = config.get_connection_string()

        assert connection_string == connection_url

    def test_get_connection_string_sqlserver_no_port(self):
        """Test SQL Server connection string generation without port."""
        config = DatabaseConfig(
            server="sqlserver",
            host="localhost",
            database="testdb",
            username="testuser",
            password="testpass",
        )

        connection_string = config.get_connection_string()

        assert "SERVER=localhost" in connection_string
        assert "SERVER=localhost," not in connection_string

    def test_get_connection_string_unsupported_server(self):
        """Test connection string generation for unsupported server."""
        with pytest.raises(ValueError, match="Unsupported server type"):
            DatabaseConfig(
                server="oracle",
                host="localhost",
                database="testdb",
                username="user",
                password="pass",
            )
