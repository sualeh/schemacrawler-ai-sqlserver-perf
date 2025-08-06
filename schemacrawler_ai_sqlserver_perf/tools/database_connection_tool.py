"""Database connection MCP tool."""

import logging
from typing import Any

from schemacrawler_ai_sqlserver_perf.database import execute_sql_template

logger = logging.getLogger(__name__)

# SQL template for getting database connection information
DATABASE_INFO_SQL_TEMPLATE = """
SELECT
    @@VERSION as version,
    SERVERPROPERTY('ProductName') as product_name,
    SERVERPROPERTY('ProductVersion') as product_version
"""


async def database_connection_tool() -> dict[str, Any]:
    """
    Makes a fresh connection to the database and returns the raw data.

    Returns:
        JSON object with raw database data
    """
    try:
        # Execute SQL template to get database information
        result = execute_sql_template(DATABASE_INFO_SQL_TEMPLATE)

        if result["success"]:
            # Return data as-is: empty list if no data, or the actual data list
            data = result["data"] if result["data"] else []

            return {
                "message": "Database connection successful",
                "data": data,
                "connection_status": "connected",
                "success": True,
            }
        else:
            # SQL execution failed
            return {
                "message": f"Database connection failed: {result['error']}",
                "data": [],
                "connection_status": "failed",
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Database connection tool failed: %s", e)
        return {
            "message": f"Database connection tool failed: {str(e)}",
            "data": [],
            "connection_status": "failed",
            "error": str(e),
            "success": False,
        }
