"""Performance monitoring MCP tools for SQL Server."""

import logging
from typing import Any

from schemacrawler_ai_sqlserver_perf.database import execute_sql_template

logger = logging.getLogger(__name__)

# SQL template for monitoring live activity and blocking
LIVE_ACTIVITY_BLOCKING_SQL_TEMPLATE = """
SELECT
  t.text AS query_text,
  r.session_id AS blocked_session,
  r.blocking_session_id AS blocker_session,
  r.status,
  r.wait_type,
  r.wait_time,
  r.cpu_time,
  r.total_elapsed_time
FROM sys.dm_exec_requests r
JOIN sys.dm_exec_sessions s ON r.session_id = s.session_id
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.blocking_session_id <> 0;
"""

# SQL template for finding cached plans with reuse info
CACHED_PLANS_REUSE_SQL_TEMPLATE = """
SELECT TOP 100
  st.text AS query_text,
  cp.usecounts,
  cp.cacheobjtype,
  cp.objtype,
  cp.size_in_bytes / 1024 AS size_kb
FROM sys.dm_exec_cached_plans cp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
WHERE cp.cacheobjtype = 'Compiled Plan'
ORDER BY cp.usecounts DESC;
"""

# SQL template for detecting plan cache bloat
PLAN_CACHE_BLOAT_SQL_TEMPLATE = """
SELECT
  st.text AS query_text,
  cp.usecounts,
  cp.size_in_bytes / 1024 AS size_kb,
  cp.objtype
FROM sys.dm_exec_cached_plans cp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
WHERE cp.objtype = 'Adhoc'
  AND cp.usecounts = 1
ORDER BY cp.size_in_bytes DESC;
"""

# SQL template for finding active blocking & waits
ACTIVE_BLOCKING_WAITS_SQL_TEMPLATE = """
SELECT
  t.text AS query_text,
  r.session_id,
  r.blocking_session_id,
  r.status,
  r.wait_type,
  r.wait_time,
  r.cpu_time,
  r.total_elapsed_time
FROM sys.dm_exec_requests r
JOIN sys.dm_exec_sessions s ON r.session_id = s.session_id
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.blocking_session_id <> 0;
"""

# SQL template for detecting lock contention
LOCK_CONTENTION_SQL_TEMPLATE = """
SELECT
  t.text AS query_text,
  tl.resource_type,
  tl.resource_database_id,
  tl.resource_associated_entity_id,
  tl.request_mode,
  tl.request_status,
  s.session_id,
  s.login_name
FROM sys.dm_tran_locks tl
JOIN sys.dm_exec_sessions s ON tl.request_session_id = s.session_id
JOIN sys.dm_exec_requests r ON s.session_id = r.session_id
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t;
"""

# SQL template for analyzing wait statistics
WAIT_STATISTICS_SQL_TEMPLATE = """
SELECT TOP 20
    wait_type,
    wait_time_ms / 1000.0 AS wait_time_sec,
    waiting_tasks_count,
    wait_time_ms/ (1000 * waiting_tasks_count) AS avg_wait_time_sec
FROM sys.dm_os_wait_stats
WHERE wait_type NOT LIKE '%SLEEP%'
AND waiting_tasks_count > 0
ORDER BY wait_time_ms DESC;
"""


async def monitor_live_activity_blocking() -> dict[str, Any]:
    """
    Identify currently executing SQL requests that are being blocked by another session.

    This tool shows active SQL Server sessions that are experiencing blocking, providing
    insight into real-time contention. It displays the blocked session, the blocker session,
    the SQL query being executed, and wait information.

    Data Sources:
        - sys.dm_exec_requests: Current executing requests with blocking details
        - sys.dm_exec_sessions: Session metadata for joining and filtering
        - sys.dm_exec_sql_text: Full SQL text for each request

    Returns:
        JSON object containing:
        - query_text: The exact SQL statement being executed by the blocked session
        - blocked_session: ID of the session experiencing blocking
        - blocker_session: ID of the session causing the block
        - status: Execution status (e.g., running, suspended)
        - wait_type: Type of resource being waited on (e.g., LCK_M_IX)
        - wait_time: Duration in milliseconds the session has been waiting
        - cpu_time: Total CPU time consumed by the session
        - total_elapsed_time: Wall-clock time since the request started
    """
    try:
        result = execute_sql_template(LIVE_ACTIVITY_BLOCKING_SQL_TEMPLATE)

        if result["success"]:
            data = result["data"] if result["data"] else []

            return {
                "message": "Live activity and blocking information retrieved successfully",
                "data": data,
                "row_count": len(data),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to retrieve live activity and blocking information: {result['error']}",
                "data": [],
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Monitor live activity and blocking tool failed: %s", e)
        return {
            "message": f"Monitor live activity and blocking tool failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "error": str(e),
            "success": False,
        }


async def find_cached_plans_reuse() -> dict[str, Any]:
    """
    Examine the top 100 most frequently reused compiled query plans in the SQL Server plan cache.

    This tool identifies the most reused query execution plans, which is valuable for understanding
    plan cache efficiency and frequently executed query patterns. High reuse counts indicate
    well-parameterized queries that benefit from plan caching.

    Data Sources:
        - sys.dm_exec_cached_plans: Metadata about cached query and object plans
        - sys.dm_exec_sql_text: Raw SQL text corresponding to cached plans

    Returns:
        JSON object containing:
        - query_text: Full SQL text associated with the compiled plan
        - usecounts: Number of times the plan has been reused from the cache
        - cacheobjtype: Type of cached object (filtered to 'Compiled Plan')
        - objtype: Object type (e.g., 'Adhoc', 'Prepared', 'Proc')
        - size_kb: Size of the cached plan in kilobytes
    """
    try:
        result = execute_sql_template(CACHED_PLANS_REUSE_SQL_TEMPLATE)

        if result["success"]:
            data = result["data"] if result["data"] else []

            return {
                "message": "Cached plans with reuse information retrieved successfully",
                "data": data,
                "row_count": len(data),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to retrieve cached plans with reuse information: {result['error']}",
                "data": [],
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Find cached plans with reuse tool failed: %s", e)
        return {
            "message": f"Find cached plans with reuse tool failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "error": str(e),
            "success": False,
        }


async def detect_plan_cache_bloat() -> dict[str, Any]:
    """
    Identify one-time-use ad hoc queries occupying significant space in the SQL Server plan cache.

    This tool helps detect plan cache bloat caused by poorly parameterized or one-off queries.
    These plans consume memory but provide no performance benefit since they're never reused.
    This information can guide cleanup strategies and parameterization improvements.

    Data Sources:
        - sys.dm_exec_cached_plans: Cached execution plans with usage count and plan size
        - sys.dm_exec_sql_text: Original SQL text using the plan handle

    Filtering Logic:
        - Restricts to 'Adhoc' object types (unparameterized statements)
        - Filters for usecounts = 1 (plans used only once)

    Returns:
        JSON object containing:
        - query_text: Full SQL statement associated with the plan
        - usecounts: Number of times the plan has been reused (always 1)
        - size_kb: Size of the cached plan in kilobytes
        - objtype: Object type (filtered to 'Adhoc')
    """
    try:
        result = execute_sql_template(PLAN_CACHE_BLOAT_SQL_TEMPLATE)

        if result["success"]:
            data = result["data"] if result["data"] else []

            return {
                "message": "Plan cache bloat information retrieved successfully",
                "data": data,
                "row_count": len(data),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to retrieve plan cache bloat information: {result['error']}",
                "data": [],
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Detect plan cache bloat tool failed: %s", e)
        return {
            "message": f"Detect plan cache bloat tool failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "error": str(e),
            "success": False,
        }


async def find_active_blocking_waits() -> dict[str, Any]:
    """
    Identify active SQL Server sessions that are currently blocked by other sessions.

    This tool provides real-time visibility into blocking scenarios that could lead to
    performance degradation or deadlocks. It shows the complete picture of blocked sessions
    including their SQL queries, wait types, and timing information.

    Data Sources:
        - sys.dm_exec_requests: All currently executing requests with blocking metadata
        - sys.dm_exec_sessions: Session-level context and connection details
        - sys.dm_exec_sql_text: Full SQL text associated with executing requests

    Returns:
        JSON object containing:
        - query_text: Full SQL query that the blocked session is trying to execute
        - session_id: ID of the currently executing (blocked) session
        - blocking_session_id: ID of the session causing the block
        - status: Execution status (e.g., 'suspended', 'running')
        - wait_type: Type of resource being waited on (e.g., lock, latch)
        - wait_time: Duration in milliseconds the session has been blocked
        - cpu_time: Total processor time used by the session
        - total_elapsed_time: Wall-clock duration of the current request
    """
    try:
        result = execute_sql_template(ACTIVE_BLOCKING_WAITS_SQL_TEMPLATE)

        if result["success"]:
            data = result["data"] if result["data"] else []

            return {
                "message": "Active blocking and waits information retrieved successfully",
                "data": data,
                "row_count": len(data),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to retrieve active blocking and waits information: {result['error']}",
                "data": [],
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Find active blocking and waits tool failed: %s", e)
        return {
            "message": f"Find active blocking and waits tool failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "error": str(e),
            "success": False,
        }


async def detect_lock_contention() -> dict[str, Any]:
    """
    Retrieve detailed information about currently held transactional locks with session context.

    This tool provides comprehensive lock analysis by showing all current lock requests along with
    the SQL queries and sessions responsible for them. It's essential for diagnosing lock
    contention, lock escalation issues, and understanding transaction scope impacts.

    Data Sources:
        - sys.dm_tran_locks: Lock-level metadata for all held and pending lock requests
        - sys.dm_exec_sessions: Session information including login names
        - sys.dm_exec_requests: Executing requests for active sessions
        - sys.dm_exec_sql_text: SQL statements associated with lock requests

    Returns:
        JSON object containing:
        - query_text: SQL query responsible for the lock request
        - resource_type: Type of locked resource (e.g., OBJECT, PAGE, KEY)
        - resource_database_id: ID of the database where the resource resides
        - resource_associated_entity_id: Internal identifier of the locked object
        - request_mode: Lock mode (e.g., SHARED, EXCLUSIVE, INTENT)
        - request_status: Current state of the lock request (e.g., GRANTED, WAIT)
        - session_id: ID of the session holding or requesting the lock
        - login_name: Login name associated with the session
    """
    try:
        result = execute_sql_template(LOCK_CONTENTION_SQL_TEMPLATE)

        if result["success"]:
            data = result["data"] if result["data"] else []

            return {
                "message": "Lock contention information retrieved successfully",
                "data": data,
                "row_count": len(data),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to retrieve lock contention information: {result['error']}",
                "data": [],
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Detect lock contention tool failed: %s", e)
        return {
            "message": f"Detect lock contention tool failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "error": str(e),
            "success": False,
        }


async def analyze_wait_statistics() -> dict[str, Any]:
    """
    Analyze SQL Server wait statistics to identify the most time-consuming wait types.

    This tool provides server-wide wait analysis to identify performance bottlenecks such as
    locking, latching, I/O waits, or thread scheduling issues. It shows cumulative wait statistics
    since the last service restart or statistics clearance.

    Data Source:
        - sys.dm_os_wait_stats: Accumulated wait times and task counts for various wait types

    Filtering Logic:
        - Excludes wait types containing 'SLEEP' (idle or background waits)
        - Excludes rows where waiting_tasks_count = 0 (non-informative entries)

    Returns:
        JSON object containing:
        - wait_type: Description of the wait category (e.g., LCK_M_IX, PAGEIOLATCH_SH)
        - wait_time_sec: Total time spent on this wait type (in seconds)
        - waiting_tasks_count: Number of tasks that encountered this wait
        - avg_wait_time_sec: Average time a task spends waiting on this wait type (in seconds)
    """
    try:
        result = execute_sql_template(WAIT_STATISTICS_SQL_TEMPLATE)

        if result["success"]:
            data = result["data"] if result["data"] else []

            return {
                "message": "Wait statistics information retrieved successfully",
                "data": data,
                "row_count": len(data),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to retrieve wait statistics information: {result['error']}",
                "data": [],
                "row_count": 0,
                "error": result["error"],
                "success": False,
            }

    except Exception as e:
        logger.error("Analyze wait statistics tool failed: %s", e)
        return {
            "message": f"Analyze wait statistics tool failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "error": str(e),
            "success": False,
        }
