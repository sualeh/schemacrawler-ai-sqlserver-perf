"""Database connection MCP tool."""

import datetime
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
    Makes a fresh connection to the database and prints basic database information
    such as the database product name and version.

    Returns:
        JSON object with database connection information
    """
    try:
        # Execute SQL template to get database information
        result = execute_sql_template(DATABASE_INFO_SQL_TEMPLATE)
        
        if result["success"] and result["data"]:
            # Extract database information from the first row
            db_info = result["data"][0]
            
            version_string = db_info.get("version", "").strip() if db_info.get("version") else "Unknown"
            product_name = db_info.get("product_name", "").strip() if db_info.get("product_name") else "Unknown"
            product_version = db_info.get("product_version", "").strip() if db_info.get("product_version") else "Unknown"

            # Extract first line of version string for cleaner output
            version_first_line = version_string.split('\n')[0] if version_string else "Unknown"

            return {
                "message": "Database connection successful",
                "database_info": {
                    "product_name": product_name,
                    "product_version": product_version,
                    "version_string": version_first_line,
                    "full_version": version_string
                },
                "connection_status": "connected",
                "timestamp": datetime.datetime.now(datetime.UTC)
                    .isoformat()
                    .replace("+00:00", "Z"),
                "tool": "database_connection",
                "success": True,
            }
        elif result["success"] and not result["data"]:
            return {
                "message": "Database connection successful but no version information available",
                "database_info": {
                    "product_name": "Unknown",
                    "product_version": "Unknown",
                    "version_string": "Unknown"
                },
                "connection_status": "connected",
                "timestamp": datetime.datetime.now(datetime.UTC)
                    .isoformat()
                    .replace("+00:00", "Z"),
                "tool": "database_connection",
                "success": True,
            }
        else:
            # SQL execution failed
            return {
                "message": f"Database connection failed: {result['error']}",
                "database_info": None,
                "connection_status": "failed",
                "error": result["error"],
                "timestamp": datetime.datetime.now(datetime.UTC)
                    .isoformat()
                    .replace("+00:00", "Z"),
                "tool": "database_connection",
                "success": False,
            }

    except Exception as e:
        logger.error("Database connection tool failed: %s", e)
        return {
            "message": f"Database connection tool failed: {str(e)}",
            "database_info": None,
            "connection_status": "failed",
            "error": str(e),
            "timestamp": datetime.datetime.now(datetime.UTC)
                .isoformat()
                .replace("+00:00", "Z"),
            "tool": "database_connection",
            "success": False,
        }
