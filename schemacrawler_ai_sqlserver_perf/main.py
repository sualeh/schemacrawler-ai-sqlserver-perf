"""Main entry point for the SchemaCrawler AI MCP Server."""

import logging
import sys

import fastmcp

from schemacrawler_ai_sqlserver_perf.tools.version_tool import version_tool
from schemacrawler_ai_sqlserver_perf.database import validate_database_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server() -> fastmcp.FastMCP:
    """Create and configure the MCP server."""
    # Validate database connection before starting server
    logger.info("Validating database connection...")
    
    if not validate_database_connection():
        logger.error("Database connection validation failed. Server cannot start.")
        sys.exit(1)
    
    logger.info("Database connection validation successful")
    
    # Create FastMCP server instance
    server = fastmcp.FastMCP(
        "SchemaCrawler AI MCP Server for SQL Server Performance"
    )

    # Register the hello world tool using the decorator
    server.tool()(version_tool)

    logger.info("SchemaCrawler AI MCP Server for SQL Server Performance initialized")
    return server


if __name__ == "__main__":
    """Main entry point for the server."""
    server = create_server()

    # Run the server
    server.run(transport="stdio")
