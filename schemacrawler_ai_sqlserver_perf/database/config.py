"""Database configuration module for environment variable handling."""

import os
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DatabaseConfig(BaseModel):
    """Database configuration from environment variables."""

    # Connection parameters
    server: Optional[str] = Field(
        None, description="Database server type (e.g., sqlserver)"
    )
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")

    # Connection URL (alternative to individual parameters)
    connection_url: Optional[str] = Field(
        None, description="Database connection URL"
    )

    # Credentials (required)
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")

    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""

        # Get credentials
        # If credentials are required, they must be set
        username = os.getenv("SCHCRWLR_DATABASE_USER")
        password = os.getenv("SCHCRWLR_DATABASE_PASSWORD")

        if not username or not password:
            raise ValueError(
                "Database credentials are required: "
                "SCHCRWLR_DATABASE_USER and SCHCRWLR_DATABASE_PASSWORD"
            )

        # Get connection URL if provided
        connection_url = os.getenv("SCHCRWLR_CONNECTION_URL")

        if connection_url:
            # Use connection URL directly without parsing
            return cls(
                connection_url=connection_url,
                username=username,
                password=password,
            )
        else:
            # Get individual connection parameters
            server = os.getenv("SCHCRWLR_SERVER")
            host = os.getenv("SCHCRWLR_HOST")
            port_str = os.getenv("SCHCRWLR_PORT")
            database = os.getenv("SCHCRWLR_DATABASE")

            # Validate required parameters
            if not all([server, host, database]):
                raise ValueError(
                    "Either SCHCRWLR_CONNECTION_URL or all of the following "
                    "are required: SCHCRWLR_SERVER, SCHCRWLR_HOST, "
                    "SCHCRWLR_DATABASE"
                )

            port = int(port_str) if port_str else None

            return cls(
                server=server,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
            )

    @field_validator("server")
    @classmethod
    def validate_server(cls, v):
        """Validate server type."""
        if v and v.lower() not in ["sqlserver"]:
            raise ValueError(
                f"Unsupported server type: {v}. Only 'sqlserver' is currently "
                "supported."
            )
        return v.lower() if v else v

    def get_connection_string(self) -> str:
        """Generate a connection string for the database."""
        if self.connection_url:
            # Use the connection URL directly as ODBC connection string
            return self.connection_url
        elif self.server == "sqlserver":
            return self._get_sqlserver_connection_string()
        else:
            raise ValueError(f"Unsupported server type: {self.server}")

    def _get_sqlserver_connection_string(self) -> str:
        """Generate SQL Server ODBC connection string for pyodbc."""
        parts = []

        # Driver - use ODBC Driver for SQL Server
        parts.append("DRIVER={ODBC Driver 18 for SQL Server}")

        # Server
        if self.port:
            parts.append(f"SERVER={self.host},{self.port}")
        else:
            parts.append(f"SERVER={self.host}")

        # Database
        parts.append(f"DATABASE={self.database}")

        # Authentication
        parts.append(f"UID={self.username}")
        parts.append(f"PWD={self.password}")

        # Additional settings for better compatibility
        # parts.append("Encrypt=yes")
        parts.append("TrustServerCertificate=yes")
        parts.append("SSLProtocol=TLSv1.2")

        return ";".join(parts)
