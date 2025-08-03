"""Main entry point for the SchemaCrawler AI MCP Server."""

import asyncio
import logging

from mcp.server import FastMCP

from schemacrawler_ai.tools.hello_world import hello_world_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    # Create FastMCP server instance
    server = FastMCP("SchemaCrawler AI MCP Server for SQL Server Performance")

    # Register the hello world tool using the decorator
    server.tool()(hello_world_tool)

    logger.info("SchemaCrawler AI MCP Server for SQL Server Performance initialized")
    return server


def main() -> None:
    """Main entry point for the server."""
    server = create_server()

    # Run the server
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
