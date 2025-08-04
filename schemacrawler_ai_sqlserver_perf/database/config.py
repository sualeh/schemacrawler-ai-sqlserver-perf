"""Database configuration module for environment variable handling."""

import os
import re
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class DatabaseConfig(BaseModel):
    """Database configuration from environment variables."""
    
    # Connection parameters
    server: Optional[str] = Field(None, description="Database server type (e.g., sqlserver)")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")
    
    # JDBC URL (alternative to individual parameters)
    jdbc_url: Optional[str] = Field(None, description="JDBC connection URL")
    
    # Credentials (required)
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    
    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""
        
        # Get credentials (required)
        username = os.getenv("SCHCRWLR_DATABASE_USER")
        password = os.getenv("SCHCRWLR_DATABASE_PASSWORD")
        
        if not username or not password:
            raise ValueError(
                "Database credentials are required: "
                "SCHCRWLR_DATABASE_USER and SCHCRWLR_DATABASE_PASSWORD"
            )
        
        # Get JDBC URL if provided
        jdbc_url = os.getenv("SCHCRWLR_JDBC_URL")
        
        if jdbc_url:
            # Parse JDBC URL to extract connection parameters
            server, host, port, database = cls._parse_jdbc_url(jdbc_url)
            return cls(
                jdbc_url=jdbc_url,
                server=server,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password
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
                    "Either SCHCRWLR_JDBC_URL or all of the following are required: "
                    "SCHCRWLR_SERVER, SCHCRWLR_HOST, SCHCRWLR_DATABASE"
                )
            
            port = int(port_str) if port_str else None
            
            return cls(
                server=server,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password
            )
    
    @staticmethod
    def _parse_jdbc_url(jdbc_url: str) -> tuple[str, str, Optional[int], str]:
        """Parse JDBC URL to extract connection parameters.
        
        Supports formats like:
        - jdbc:sqlserver://host:port;databaseName=dbname
        - jdbc:sqlserver://host;databaseName=dbname
        """
        if not jdbc_url.startswith("jdbc:"):
            raise ValueError(f"Invalid JDBC URL format: {jdbc_url}")
        
        # Remove jdbc: prefix and extract the database type
        url_without_jdbc = jdbc_url[5:]  # Remove "jdbc:"
        
        # Parse the database type (e.g., "sqlserver")
        if "://" not in url_without_jdbc:
            raise ValueError(f"Invalid JDBC URL format: {jdbc_url}")
        
        server_type, connection_part = url_without_jdbc.split("://", 1)
        
        # Parse SQL Server format: host:port;databaseName=dbname
        if server_type == "sqlserver":
            # Split on semicolon to separate host:port from properties
            if ";" in connection_part:
                host_port_part, properties_part = connection_part.split(";", 1)
                
                # Extract database name from properties
                database = None
                for prop in properties_part.split(";"):
                    if prop.startswith("databaseName="):
                        database = prop.split("=", 1)[1]
                        break
                
                if not database:
                    raise ValueError(f"No databaseName found in JDBC URL: {jdbc_url}")
                
                # Parse host and port
                if ":" in host_port_part:
                    host, port_str = host_port_part.rsplit(":", 1)
                    try:
                        port = int(port_str)
                    except ValueError:
                        raise ValueError(f"Invalid port in JDBC URL: {jdbc_url}")
                else:
                    host = host_port_part
                    port = None
                
                return server_type, host, port, database
            else:
                raise ValueError(f"Invalid SQL Server JDBC URL format: {jdbc_url}")
        else:
            raise ValueError(f"Unsupported database type in JDBC URL: {server_type}")
    
    @field_validator("server")
    @classmethod
    def validate_server(cls, v):
        """Validate server type."""
        if v and v.lower() not in ["sqlserver"]:
            raise ValueError(f"Unsupported server type: {v}. Only 'sqlserver' is currently supported.")
        return v.lower() if v else v
    
    def get_connection_string(self) -> str:
        """Generate a connection string for the database."""
        if self.server == "sqlserver":
            return self._get_sqlserver_connection_string()
        else:
            raise ValueError(f"Unsupported server type: {self.server}")
    
    def _get_sqlserver_connection_string(self) -> str:
        """Generate SQL Server connection string for pyodbc."""
        parts = []
        
        # Driver - use ODBC Driver 17 for SQL Server (most common)
        parts.append("DRIVER={ODBC Driver 17 for SQL Server}")
        
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
        parts.append("Encrypt=yes")
        parts.append("TrustServerCertificate=yes")
        
        return ";".join(parts)