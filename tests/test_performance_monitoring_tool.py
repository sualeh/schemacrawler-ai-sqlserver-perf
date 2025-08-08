"""Tests for performance monitoring tools SQL templates."""

from schemacrawler_ai_sqlserver_perf.tools.performance_monitoring_tool import (
    LIVE_ACTIVITY_BLOCKING_SQL_TEMPLATE,
    CACHED_PLANS_REUSE_SQL_TEMPLATE,
    PLAN_CACHE_BLOAT_SQL_TEMPLATE,
    ACTIVE_BLOCKING_WAITS_SQL_TEMPLATE,
    LOCK_CONTENTION_SQL_TEMPLATE,
    WAIT_STATISTICS_SQL_TEMPLATE,
)


class TestPerformanceMonitoringTool:
    """Test suite for performance_monitoring_tool."""

    def test_live_activity_blocking_sql_template(self):
        """Test live activity and blocking SQL template structure."""
        sql = LIVE_ACTIVITY_BLOCKING_SQL_TEMPLATE
        assert isinstance(sql, str)
        assert len(sql.strip()) > 0

        # Check for essential components
        assert "sys.dm_exec_requests" in sql
        assert "sys.dm_exec_sessions" in sql
        assert "sys.dm_exec_sql_text" in sql
        assert "blocking_session_id" in sql
        assert "WHERE r.blocking_session_id <> 0" in sql

    def test_cached_plans_reuse_sql_template(self):
        """Test cached plans with reuse info SQL template structure."""
        sql = CACHED_PLANS_REUSE_SQL_TEMPLATE
        assert isinstance(sql, str)
        assert len(sql.strip()) > 0

        # Check for essential components
        assert "TOP 100" in sql
        assert "sys.dm_exec_cached_plans" in sql
        assert "sys.dm_exec_sql_text" in sql
        assert "usecounts" in sql
        assert "cacheobjtype = 'Compiled Plan'" in sql
        assert "ORDER BY cp.usecounts DESC" in sql

    def test_plan_cache_bloat_sql_template(self):
        """Test plan cache bloat detection SQL template structure."""
        sql = PLAN_CACHE_BLOAT_SQL_TEMPLATE
        assert isinstance(sql, str)
        assert len(sql.strip()) > 0

        # Check for essential components
        assert "sys.dm_exec_cached_plans" in sql
        assert "sys.dm_exec_sql_text" in sql
        assert "objtype = 'Adhoc'" in sql
        assert "usecounts = 1" in sql
        assert "ORDER BY cp.size_in_bytes DESC" in sql

    def test_active_blocking_waits_sql_template(self):
        """Test active blocking and waits SQL template structure."""
        sql = ACTIVE_BLOCKING_WAITS_SQL_TEMPLATE
        assert isinstance(sql, str)
        assert len(sql.strip()) > 0

        # Check for essential components
        assert "sys.dm_exec_requests" in sql
        assert "sys.dm_exec_sessions" in sql
        assert "sys.dm_exec_sql_text" in sql
        assert "blocking_session_id" in sql
        assert "WHERE r.blocking_session_id <> 0" in sql

    def test_lock_contention_sql_template(self):
        """Test lock contention detection SQL template structure."""
        sql = LOCK_CONTENTION_SQL_TEMPLATE
        assert isinstance(sql, str)
        assert len(sql.strip()) > 0

        # Check for essential components
        assert "sys.dm_tran_locks" in sql
        assert "sys.dm_exec_sessions" in sql
        assert "sys.dm_exec_requests" in sql
        assert "sys.dm_exec_sql_text" in sql
        assert "resource_type" in sql
        assert "request_mode" in sql
        assert "request_status" in sql

    def test_wait_statistics_sql_template(self):
        """Test wait statistics analysis SQL template structure."""
        sql = WAIT_STATISTICS_SQL_TEMPLATE
        assert isinstance(sql, str)
        assert len(sql.strip()) > 0

        # Check for essential components
        assert "TOP 20" in sql
        assert "sys.dm_os_wait_stats" in sql
        assert "wait_type" in sql
        assert "wait_time_ms" in sql
        assert "waiting_tasks_count" in sql
        assert "WHERE wait_type NOT LIKE '%SLEEP%'" in sql
        assert "AND waiting_tasks_count > 0" in sql
        assert "ORDER BY wait_time_ms DESC" in sql

    def test_all_templates_are_strings(self):
        """Test that all SQL templates are non-empty strings."""
        templates = [
            LIVE_ACTIVITY_BLOCKING_SQL_TEMPLATE,
            CACHED_PLANS_REUSE_SQL_TEMPLATE,
            PLAN_CACHE_BLOAT_SQL_TEMPLATE,
            ACTIVE_BLOCKING_WAITS_SQL_TEMPLATE,
            LOCK_CONTENTION_SQL_TEMPLATE,
            WAIT_STATISTICS_SQL_TEMPLATE,
        ]

        for template in templates:
            assert isinstance(template, str)
            assert len(template.strip()) > 0

    def test_templates_contain_select_statements(self):
        """Test that all SQL templates contain SELECT statements."""
        templates = [
            LIVE_ACTIVITY_BLOCKING_SQL_TEMPLATE,
            CACHED_PLANS_REUSE_SQL_TEMPLATE,
            PLAN_CACHE_BLOAT_SQL_TEMPLATE,
            ACTIVE_BLOCKING_WAITS_SQL_TEMPLATE,
            LOCK_CONTENTION_SQL_TEMPLATE,
            WAIT_STATISTICS_SQL_TEMPLATE,
        ]

        for template in templates:
            assert "SELECT" in template.upper()
