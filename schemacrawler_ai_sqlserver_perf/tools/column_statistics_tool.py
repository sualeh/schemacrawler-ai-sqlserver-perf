"""Column statistics MCP tool for analyzing table column statistics."""

import logging
from typing import Any

from schemacrawler_ai_sqlserver_perf.database import execute_sql_template

logger = logging.getLogger(__name__)

# SQL template for getting basic column information and table statistics
# Note: This implementation provides column metadata and table row count.
# Actual min/max/null/distinct statistics would require additional per-column queries
# which could be added in future iterations based on performance requirements.
COLUMN_STATISTICS_SQL_TEMPLATE = """
WITH TableStats AS (
    SELECT COUNT(*) as total_rows
    FROM [{{database_name}}].[{{schema_name}}].[{{table_name}}]
),
ColumnInfo AS (
    SELECT 
        '{{database_name}}' as database_name,
        '{{schema_name}}' as schema_name,
        '{{table_name}}' as table_name,
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.IS_NULLABLE,
        c.CHARACTER_MAXIMUM_LENGTH,
        c.NUMERIC_PRECISION,
        c.NUMERIC_SCALE,
        c.ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.COLUMNS c
    WHERE c.TABLE_CATALOG = '{{database_name}}'
      AND c.TABLE_SCHEMA = '{{schema_name}}'
      AND c.TABLE_NAME = '{{table_name}}'
)
SELECT 
    ci.*,
    ts.total_rows as total_count,
    -- TODO: Future enhancement - calculate actual column statistics
    -- These would require per-column dynamic queries for optimal performance
    CAST(NULL AS VARCHAR(255)) as min_value,
    CAST(NULL AS VARCHAR(255)) as max_value,
    CAST(NULL AS BIGINT) as null_count,
    CAST(NULL AS BIGINT) as distinct_count
FROM ColumnInfo ci
CROSS JOIN TableStats ts
ORDER BY ci.ORDINAL_POSITION
"""


async def column_statistics_tool(
    database_name: str, schema_name: str, table_name: str
) -> dict[str, Any]:
    """
    Get column statistics for a specific table including column metadata and table row count.
    
    This tool provides:
    - Column metadata (name, data type, nullable, precision, etc.)
    - Table total row count
    - Structure for future statistical calculations (min/max/null/distinct counts)

    Args:
        database_name: The name of the database (will be shown in INFORMATION_SCHEMA format)
        schema_name: The name of the schema (will be shown in INFORMATION_SCHEMA format)
        table_name: The name of the table (will be shown in INFORMATION_SCHEMA format)

    Returns:
        JSON object with column statistics data including database_name, schema_name, 
        and table_name in separate columns in INFORMATION_SCHEMA format for easy identification
    """
    try:
        # Prepare substitutions for the SQL template
        substitutions = {
            "database_name": database_name,
            "schema_name": schema_name,
            "table_name": table_name,
        }

        # Execute SQL template to get column statistics
        result = execute_sql_template(COLUMN_STATISTICS_SQL_TEMPLATE, substitutions)

        if result["success"]:
            # Return data as-is: empty list if no data, or the actual data list
            data = result["data"] if result["data"] else []

            return {
                "message": f"Column statistics retrieved successfully for {database_name}.{schema_name}.{table_name}",
                "data": data,
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
                "column_count": len(data),
                "success": True,
            }
        else:
            # SQL execution failed
            return {
                "message": f"Failed to retrieve column statistics for {database_name}.{schema_name}.{table_name}: {result['error']}",
                "data": [],
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
                "column_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Column statistics tool failed: %s", e)
        return {
            "message": f"Column statistics tool failed: {str(e)}",
            "data": [],
            "database_name": database_name,
            "schema_name": schema_name,
            "table_name": table_name,
            "column_count": 0,
            "error": str(e),
            "success": False,
        }