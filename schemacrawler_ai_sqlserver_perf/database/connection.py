"""Database connection management for SchemaCrawler AI SQL Server Performance Analysis."""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

try:
    import pyodbc
except ImportError:
    pyodbc = None

from .config import DatabaseConfig


logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize with database configuration."""
        self.config = config
        self._connection: Optional[pyodbc.Connection] = None
    
    def connect(self) -> pyodbc.Connection:
        """Establish database connection."""
        if pyodbc is None:
            raise ImportError(
                "pyodbc is required for SQL Server connections. "
                "Install it with: pip install pyodbc"
            )
        
        connection_string = self.config.get_connection_string()
        logger.info(f"Connecting to {self.config.server} database at {self.config.host}")
        
        try:
            self._connection = pyodbc.connect(connection_string)
            logger.info("Database connection established successfully")
            return self._connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                self._connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                self._connection = None
    
    def validate_connection(self) -> bool:
        """Validate database connection by executing a simple query."""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Execute a simple query to validate connection
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            self.disconnect()
            
            return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Database connection validation failed: {e}")
            return False
    
    @contextmanager
    def get_connection(self) -> Generator[pyodbc.Connection, None, None]:
        """Context manager for database connections."""
        connection = None
        try:
            connection = self.connect()
            yield connection
        finally:
            if connection:
                self.disconnect()
    
    def __enter__(self) -> pyodbc.Connection:
        """Context manager entry."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()


def create_connection(config: Optional[DatabaseConfig] = None) -> DatabaseConnection:
    """Create a database connection from configuration.
    
    Args:
        config: Database configuration. If None, reads from environment variables.
    
    Returns:
        DatabaseConnection instance
    
    Raises:
        ValueError: If configuration is invalid
        ImportError: If required database drivers are not installed
    """
    if config is None:
        config = DatabaseConfig.from_environment()
    
    return DatabaseConnection(config)


def validate_database_connection() -> bool:
    """Validate database connection using environment configuration.
    
    Returns:
        True if connection is valid, False otherwise
    """
    try:
        connection = create_connection()
        return connection.validate_connection()
    except Exception as e:
        logger.error(f"Database connection validation failed: {e}")
        return False