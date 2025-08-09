"""Main entry point for the SchemaCrawler AI MCP Server."""

import logging
import os
import sys

import fastmcp

from schemacrawler_ai_sqlserver_perf.tools.database_connection_tool import (
    database_connection_tool,
)
from schemacrawler_ai_sqlserver_perf.tools.top_queries_tool import (
    top_queries_tool,
)
from schemacrawler_ai_sqlserver_perf.tools.performance_monitoring_tool import (
    monitor_live_activity_blocking,
    find_cached_plans_reuse,
    detect_plan_cache_bloat,
    find_active_blocking_waits,
    detect_lock_contention,
    analyze_wait_statistics,
)
from schemacrawler_ai_sqlserver_perf.database import validate_database_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHOULD_VALIDATE_ENVIRONMENT = (
    os.getenv("SHOULD_VALIDATE_ENVIRONMENT", "false").lower() == "true"
)


def validate_environment() -> None:
    """Validate the environment before starting the server."""
    if not validate_database_connection():
        logger.error("Database connection validation failed.")
        sys.exit(1)
    logger.info("Environment validation successful.")


def create_server() -> fastmcp.FastMCP:
    """Create and configure the MCP server."""

    # Create FastMCP server instance
    server = fastmcp.FastMCP("SchemaCrawler AI MCP Server for SQL Server Performance")

    # Register the tools using the decorator
    server.tool()(database_connection_tool)
    server.tool()(top_queries_tool)

    # Register performance monitoring tools
    server.tool()(monitor_live_activity_blocking)
    server.tool()(find_cached_plans_reuse)
    server.tool()(detect_plan_cache_bloat)
    server.tool()(find_active_blocking_waits)
    server.tool()(detect_lock_contention)
    server.tool()(analyze_wait_statistics)

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
