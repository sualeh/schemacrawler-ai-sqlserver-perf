"""Main entry point for the SchemaCrawler AI MCP Server."""

import logging
import sys

import fastmcp

from schemacrawler_ai_sqlserver_perf.tools.version_tool import version_tool
from schemacrawler_ai_sqlserver_perf.database import validate_database_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHOULD_VALIDATE_ENVIRONMENT = True


def validate_environment() -> None:
    """Validate the environment before starting the server."""
    if not validate_database_connection():
        logger.error("Database connection validation failed.")
        sys.exit(1)
    logger.info("Environment validation successful.")


def create_server() -> fastmcp.FastMCP:
    """Create and configure the MCP server."""

    # Create FastMCP server instance
    server = fastmcp.FastMCP(
        "SchemaCrawler AI MCP Server for SQL Server Performance"
    )

    # Register the hello world tool using the decorator
    server.tool()(version_tool)

    logger.info("SchemaCrawler AI MCP Server for SQL Server Performance initialized")
    return server


def main():
    """Main entry point for the server."""

    if SHOULD_VALIDATE_ENVIRONMENT:
        validate_environment()

    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
