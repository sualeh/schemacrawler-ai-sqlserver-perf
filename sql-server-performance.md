# SQL Server Performance Queries

## Prompt

> I am trying to understand what this means for SQL Server - "SQL performance metrics - such as query execution times, waits, resource usage are captured in DMVs which may require separate set of tools to analyze." Whare the common questions DBAs would like to get answered? What are the queries that can answer them?

## Queries

### Note on Top 10 Queries

The `ORDER BY` clause and the column being *aggregated and analyzed* in the `SELECT` clause are tied together. That’s the true pivot.

Here’s a breakdown:

| Query Focus             | Aggregated Metric                  | ORDER BY Clause             | Insight Surface                                 |
|------------------------|------------------------------------|-----------------------------|-------------------------------------------------|
| CPU-centric            | `total_worker_time / execution_count` | `ORDER BY avg_cpu_time DESC` | Most CPU-consuming per execution               |
| I/O-centric            | `total_logical_reads / execution_count` | `ORDER BY avg_logical_reads DESC` | Most memory/page-read-heavy per execution    |
| Latency-centric        | `total_elapsed_time / execution_count` | `ORDER BY avg_elapsed_time DESC` | Longest end-to-end duration per execution    |


### Top 10 by CPU Usage (Worker Time)

```sql
/*
  Purpose:
    Retrieve the top 10 SQL statements based on highest average CPU time (worker time) per execution.

  Data Sources:
    sys.dm_exec_query_stats (qs)
      - Contains runtime statistics for cached query plans.
    sys.dm_exec_sql_text (st)
      - Extracts raw SQL text from the query plan handle.

  Key Computations:
    - avg_cpu_time: Total worker time divided by execution count.
    - query_text: Substring of full SQL text corresponding to the executed statement.
      - Offsets are in bytes, hence divided by 2 to translate to NVARCHAR characters.
      - If statement_end_offset is -1 (unknown), fallback to full string length.

  Output Fields:
    - avg_cpu_time: Estimated CPU time per execution.
    - execution_count: Number of times the query was executed.
    - total_cpu_time: Aggregate CPU time for all executions.
    - query_text: Textual SQL representation extracted via plan handle.

  Ordering:
    - Sorted in descending order of avg_cpu_time to highlight most CPU-intensive queries.
*/
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
```


### Top 10 by Logical Reads

```sql
/*
  Purpose:
    Identify the top 10 SQL statements with the highest average logical read cost per execution.

  Data Sources:
    sys.dm_exec_query_stats (qs)
      - Captures query execution statistics from cached plans.
    sys.dm_exec_sql_text (st)
      - Retrieves the associated SQL text for each query via the plan handle.

  Key Computations:
    - avg_logical_reads: Total logical reads divided by execution count.
      - Reflects how I/O-intensive each execution is, based on memory page accesses.
    - query_text: Extracted substring of SQL text corresponding to the actual executed statement.
      - Offsets are byte-based, so division by 2 maps them to character offsets.
      - If end offset is -1, fallback to full text length for safety.

  Output Fields:
    - avg_logical_reads: Average memory page reads per execution.
    - execution_count: Number of times each query has run.
    - total_logical_reads: Aggregate logical reads across all executions.
    - query_text: Textual representation of the SQL fragment.

  Ordering:
    - Results sorted in descending order of avg_logical_reads to flag memory-intensive queries.
*/
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
```


### Top 10 by Elapsed Time (Duration)

```sql
/*
  Purpose:
    Extract the top 10 SQL statements with the highest average elapsed time per execution.

  Data Sources:
    sys.dm_exec_query_stats (qs)
      - Provides runtime metrics for queries cached in memory.
    sys.dm_exec_sql_text (st)
      - Retrieves the original SQL text using the query’s plan handle.

  Key Computations:
    - avg_elapsed_time: Total elapsed time divided by execution count.
      - Reflects wall-clock duration per execution, including CPU time, I/O waits, and blocking.
    - query_text: Extracted substring of SQL text from byte-based offsets.
      - Offsets are halved to convert bytes to NVARCHAR character positions.
      - If statement_end_offset is -1, use full string length as fallback.

  Output Fields:
    - avg_elapsed_time: Average wall-clock duration per execution.
    - execution_count: Total number of executions recorded.
    - total_elapsed_time: Cumulative duration for all executions.
    - query_text: Textual SQL fragment that was executed.

  Ordering:
    - Sorted by avg_elapsed_time in descending order to highlight queries with potential performance bottlenecks.
*/
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
```


### Monitor live activity and blocking

```sql
/*
  Purpose:
    Identify currently executing SQL requests that are being blocked by another session.

  Data Sources:
    sys.dm_exec_requests (r)
      - Shows current executing requests, including blocking and wait details.
    sys.dm_exec_sessions (s)
      - Provides additional session metadata for joining and filtering.
    sys.dm_exec_sql_text (t)
      - Extracts the full SQL text for each request via the plan handle.

  Filtering Logic:
    - Only includes requests where blocking_session_id is non-zero,
      indicating that the session is being blocked by another session.

  Output Fields:
    - blocked_session: ID of the session experiencing blocking.
    - blocker_session: ID of the session causing the block.
    - status: Execution status of the blocked session (e.g., running, suspended).
    - wait_type: Type of resource the session is waiting on (e.g., LCK_M_IX).
    - wait_time: Duration in milliseconds the session has been waiting.
    - cpu_time: Total CPU time consumed by the session in milliseconds.
    - total_elapsed_time: Wall-clock time since the request started.
    - sql_text: The exact SQL statement being executed by the blocked session.

  Usage:
    - Useful for diagnosing blocking chains and understanding query-level contention.
    - Can be joined with other DMVs to trace dependencies, isolation levels, or resource usage.
*/
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
```


### Cached Plans with Reuse Info

```sql
/*
  Purpose:
    Examine the top 100 most frequently reused compiled query plans in the SQL Server plan cache.

  Data Sources:
    sys.dm_exec_cached_plans (cp)
      - Contains metadata about cached query and object plans.
    sys.dm_exec_sql_text (st)
      - Retrieves the raw SQL text corresponding to a cached plan handle.

  Filtering Logic:
    - Only include entries where cacheobjtype = 'Compiled Plan',
      filtering out other cached object types like 'Parse Tree' or 'Extended Stored Procedure'.

  Output Fields:
    - query_text: Full SQL text associated with the compiled plan.
    - cacheobjtype: Type of cached object (filtered to 'Compiled Plan').
    - objtype: Specifies the object type (e.g., 'Adhoc', 'Prepared', 'Proc').
    - usecounts: Number of times the plan has been reused from the cache.
    - size_kb: Size of the cached plan in kilobytes (converted from bytes).

  Ordering:
    - Sorted by usecounts in descending order to highlight frequently executed and cached queries.

  Usage:
    - Useful for identifying highly reused query patterns and assessing plan cache health.
    - May help in tuning parameterization strategies, detecting cache bloat, or targeting candidates for forced parameterization.
*/
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
```


### Detect Plan Cache Bloat

```sql
/*
  Purpose:
    Identify one-time-use ad hoc queries occupying significant space in the SQL Server plan cache.

  Data Sources:
    sys.dm_exec_cached_plans (cp)
      - Contains metadata about cached execution plans, including usage count and plan size.
    sys.dm_exec_sql_text (st)
      - Retrieves the original SQL text using the plan handle.

  Filtering Logic:
    - Restrict to plans where objtype = 'Adhoc':
        These are typically unparameterized statements submitted directly.
    - Filter for usecounts = 1:
        Indicates the plan was used only once before being cached.

  Output Fields:
    - usecounts: Number of times the plan has been reused (always 1 in this case).
    - size_kb: Size of the cached plan in kilobytes (converted from bytes).
    - objtype: Object type, filtered to 'Adhoc'.
    - query_text: Full SQL statement associated with the plan.

  Ordering:
    - Results are sorted by size_kb descending to spotlight space-heavy single-use plans.

  Usage:
    - Helps detect cache bloat from one-off or poorly parameterized queries.
    - Can inform cleanup strategies, forced parameterization, or query design improvements.
*/
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
```

### Active Blocking & Waits

```sql
/*
  Purpose:
    Identify active SQL Server sessions that are currently blocked by other sessions.

  Data Sources:
    sys.dm_exec_requests (r)
      - Captures all currently executing requests, including performance and blocking metadata.
    sys.dm_exec_sessions (s)
      - Joins to provide session-level context such as connection details or user information.
    sys.dm_exec_sql_text (t)
      - Retrieves the full SQL text associated with the currently executing request via plan handle.

  Filtering Logic:
    - Focus only on requests where blocking_session_id is non-zero,
      meaning the session is actively waiting for a resource held by another session.

  Output Fields:
    - session_id: ID of the currently executing (blocked) session.
    - blocking_session_id: ID of the session that is causing the block.
    - status: Execution status of the blocked session (e.g., 'suspended', 'running').
    - wait_type: Type of resource the session is waiting on (e.g., lock, latch).
    - wait_time: Duration in milliseconds the session has been blocked.
    - cpu_time: Total processor time used by the session so far.
    - total_elapsed_time: Wall-clock duration of the current request.
    - sql_text: Full SQL query text that the blocked session is trying to execute.

  Usage:
    - Helps pinpoint real-time blocking scenarios that could lead to performance degradation or deadlocks.
    - Useful for tracing blocking chains and assessing query design or transaction scope.
*/
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
```


### Detect Lock Contention

```sql
/*
  Purpose:
    Retrieve detailed information about currently held transactional locks in SQL Server,
    along with the session and query-level context for each lock request.

  Data Sources:
    sys.dm_tran_locks (tl)
      - Exposes lock-level metadata for all currently held and pending lock requests.
    sys.dm_exec_sessions (s)
      - Provides session-level information such as login name and session ID.
    sys.dm_exec_requests (r)
      - Captures executing requests for active sessions, enabling association of SQL text.
    sys.dm_exec_sql_text (t)
      - Extracts the SQL statement associated with the session’s current request.

  Key Relationships:
    - tl.request_session_id links to s.session_id to correlate lock data with session context.
    - s.session_id links to r.session_id to associate executing request and plan handle.
    - CROSS APPLY retrieves SQL text from current request’s plan handle.

  Output Fields:
    - resource_type: Type of locked resource (e.g., OBJECT, PAGE, KEY).
    - resource_database_id: ID of the database where the resource resides.
    - resource_associated_entity_id: Internal identifier of the locked object or entity.
    - request_mode: Lock mode (e.g., SHARED, EXCLUSIVE, INTENT).
    - request_status: Current state of the lock request (e.g., GRANTED, WAIT).
    - session_id: ID of the session holding or requesting the lock.
    - login_name: Login name associated with the session.
    - sql_text: SQL query responsible for the lock request.

  Usage:
    - Useful for diagnosing contention, lock escalation, or transaction scope.
    - Can support visual lock trees, deadlock detection, or blocking diagnostics.
*/
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
```


### Analyze Wait Statistics

```sql
/*
  Purpose:
    Analyze SQL Server wait statistics to identify the most time-consuming types of waits across all workloads.

  Data Source:
    sys.dm_os_wait_stats
      - Tracks accumulated wait times and task counts for various wait types since last service restart or stats clearance.

  Filtering Logic:
    - Excludes wait types containing 'SLEEP' to remove idle or background waits that aren't performance-relevant.

  Key Computations:
    - wait_time_sec: Converts wait_time_ms to seconds for readability.
    - avg_wait_time_ms: Calculates average wait time per task (wait_time_ms / waiting_tasks_count).

  Output Fields:
    - wait_type: Description of the wait category (e.g., LCK_M_IX, PAGEIOLATCH_SH).
    - wait_time_sec: Total time spent on this wait type (in seconds).
    - waiting_tasks_count: Number of tasks that encountered this wait.
    - avg_wait_time_ms: Average time a task spends waiting on this wait type.

  Ordering:
    - Results sorted by wait_time_ms descending to highlight the most impactful wait types.

  Usage:
    - Provides insight into server-wide bottlenecks such as locking, latching, I/O waits, or thread scheduling.
    - Can guide index tuning, query optimization, and hardware resource assessments.
*/
SELECT TOP 20
    wait_type,
    wait_time_ms / 1000.0 AS wait_time_sec,
    waiting_tasks_count,
    wait_time_ms/ (1000 * waiting_tasks_count) AS avg_wait_time_sec
FROM sys.dm_os_wait_stats
WHERE wait_type NOT LIKE '%SLEEP%'
AND waiting_tasks_count > 0
ORDER BY wait_time_ms DESC;
```
