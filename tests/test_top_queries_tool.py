"""Tests for top queries tool."""

import pytest
from unittest.mock import patch, MagicMock


# SQL templates from the tool
SQL_TEMPLATES = {
    "cpu": """
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
""",
    "reads": """
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
""",
    "time": """
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
""",
}

from my_tool_module import SQL_TEMPLATES
class TestTopQueriesTool:
    """Test suite for top_queries_tool."""

    def test_sql_templates_exist(self):
        """Test that all required SQL templates are defined."""
        expected_metrics = ["cpu", "reads", "time"]

        for metric in expected_metrics:
            assert metric in SQL_TEMPLATES
            assert isinstance(SQL_TEMPLATES[metric], str)
            assert len(SQL_TEMPLATES[metric].strip()) > 0

    def test_sql_templates_contain_top_10(self):
        """Test that all SQL templates contain TOP 10 clause."""
        for metric, sql_template in SQL_TEMPLATES.items():
            assert (
                "TOP 10" in sql_template
            ), f"SQL template for {metric} should contain 'TOP 10'"

    def test_sql_templates_contain_order_by(self):
        """Test that all SQL templates contain ORDER BY clause."""
        for metric, sql_template in SQL_TEMPLATES.items():
            assert (
                "ORDER BY" in sql_template
            ), f"SQL template for {metric} should contain 'ORDER BY'"

    def test_sql_template_cpu_structure(self):
        """Test CPU template has correct structure."""
        sql = SQL_TEMPLATES["cpu"]
        assert "avg_cpu_time" in sql
        assert "total_worker_time" in sql
        assert "ORDER BY avg_cpu_time DESC" in sql

    def test_sql_template_reads_structure(self):
        """Test reads template has correct structure."""
        sql = SQL_TEMPLATES["reads"]
        assert "avg_logical_reads" in sql
        assert "total_logical_reads" in sql
        assert "ORDER BY avg_logical_reads DESC" in sql

    def test_sql_template_time_structure(self):
        """Test time template has correct structure."""
        sql = SQL_TEMPLATES["time"]
        assert "avg_elapsed_time" in sql
        assert "total_elapsed_time" in sql
        assert "ORDER BY avg_elapsed_time DESC" in sql
