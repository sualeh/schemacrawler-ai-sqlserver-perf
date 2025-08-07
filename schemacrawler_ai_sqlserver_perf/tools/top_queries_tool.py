"""Top 10 queries MCP tool."""

import logging
from typing import Any, Literal

from schemacrawler_ai_sqlserver_perf.database import execute_sql_template

logger = logging.getLogger(__name__)

# SQL templates for top 10 queries by different metrics
TOP_QUERIES_BY_CPU_SQL_TEMPLATE = """
SELECT TOP 10
  SUBSTRING(st.text, qs.statement_start_offset / 2,
        (CASE WHEN qs.statement_end_offset = -1
          THEN LEN(CONVERT(NVARCHAR(MAX), st.text)) * 2
          ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) AS query_text,
  qs.execution_count,
  qs.total_worker_time / qs.execution_count AS avg_cpu_time,
  qs.total_worker_time AS total_cpu_time
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY avg_cpu_time DESC;
"""

TOP_QUERIES_BY_READS_SQL_TEMPLATE = """
SELECT TOP 10
  SUBSTRING(st.text, qs.statement_start_offset / 2,
        (CASE WHEN qs.statement_end_offset = -1
          THEN LEN(CONVERT(NVARCHAR(MAX), st.text)) * 2
          ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) AS query_text,
  qs.execution_count,
  qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
  qs.total_logical_reads
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY avg_logical_reads DESC;
"""

TOP_QUERIES_BY_TIME_SQL_TEMPLATE = """
SELECT TOP 10
  SUBSTRING(st.text, qs.statement_start_offset / 2,
        (CASE WHEN qs.statement_end_offset = -1
          THEN LEN(CONVERT(NVARCHAR(MAX), st.text)) * 2
          ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) AS query_text,
  qs.execution_count,
  qs.total_elapsed_time / qs.execution_count AS avg_elapsed_time,
  qs.total_elapsed_time
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY avg_elapsed_time DESC;
"""

# Mapping of metric types to SQL templates
SQL_TEMPLATES = {
    "cpu": TOP_QUERIES_BY_CPU_SQL_TEMPLATE,
    "reads": TOP_QUERIES_BY_READS_SQL_TEMPLATE,
    "time": TOP_QUERIES_BY_TIME_SQL_TEMPLATE,
}


async def top_queries_tool(
    metric: Literal["cpu", "reads", "time"] = "cpu"
) -> dict[str, Any]:
    """
    Get the top 10 SQL queries by the specified metric.

    Args:
        metric: The performance metric to order by:
                - "cpu": Order by average CPU time (worker time) per execution
                - "reads": Order by average logical reads per execution
                - "time": Order by average elapsed time per execution

    Returns:
        JSON object with top 10 queries data
    """
    try:
        # Validate metric parameter
        if metric not in SQL_TEMPLATES:
            return {
                "message": f"Invalid metric '{metric}'. Must be one of: {list(SQL_TEMPLATES.keys())}",
                "data": [],
                "metric": metric,
                "success": False,
                "error": f"Invalid metric: {metric}",
            }

        # Get the appropriate SQL template
        sql_template = SQL_TEMPLATES[metric]

        # Execute SQL template
        result = execute_sql_template(sql_template)

        if result["success"]:
            # Return data as-is: empty list if no data, or the actual data list
            data = result["data"] if result["data"] else []

            return {
                "message": f"Top 10 queries by {metric} retrieved successfully",
                "data": data,
                "metric": metric,
                "row_count": len(data),
                "success": True,
            }
        else:
            # SQL execution failed
            return {
                "message": f"Failed to retrieve top 10 queries by {metric}: {result['error']}",
                "data": [],
                "metric": metric,
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Top queries tool failed: %s", e)
        return {
            "message": f"Top queries tool failed: {str(e)}",
            "data": [],
            "metric": metric,
            "row_count": 0,
            "error": str(e),
            "success": False,
        }
