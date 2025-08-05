"""Database connection MCP tool."""

import datetime
import logging
from typing import Any

from schemacrawler_ai_sqlserver_perf.database import create_connection

logger = logging.getLogger(__name__)


async def database_connection_tool() -> dict[str, Any]:
    """
    Makes a fresh connection to the database and prints basic database information
    such as the database product name and version.

    Returns:
        JSON object with database connection information
    """
    try:
        # Create a fresh database connection
        db_connection = create_connection()
        
        with db_connection.get_connection() as connection:
            cursor = connection.cursor()
            
            # Query for database product name and version
            cursor.execute("SELECT @@VERSION as version, SERVERPROPERTY('ProductName') as product_name, SERVERPROPERTY('ProductVersion') as product_version")
            result = cursor.fetchone()
            
            if result:
                version_string = result.version.strip() if result.version else "Unknown"
                product_name = result.product_name.strip() if result.product_name else "Unknown"
                product_version = result.product_version.strip() if result.product_version else "Unknown"
                
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
            else:
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
                
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return {
            "message": f"Database connection failed: {str(e)}",
            "database_info": None,
            "connection_status": "failed",
            "error": str(e),
            "timestamp": datetime.datetime.now(datetime.UTC)
                .isoformat()
                .replace("+00:00", "Z"),
            "tool": "database_connection",
            "success": False,
        }