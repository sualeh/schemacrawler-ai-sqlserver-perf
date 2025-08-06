"""SQL templating and execution module for SchemaCrawler AI SQL Server Performance Analysis."""

import datetime
import logging
import re
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

from .config import DatabaseConfig
from .connection import create_connection

logger = logging.getLogger(__name__)


class SQLTemplateError(Exception):
    """Exception raised for SQL template errors."""
    pass


class SQLExecutionError(Exception):
    """Exception raised for SQL execution errors."""
    pass


class SQLExecutor:
    """SQL template execution engine."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize SQL executor with database configuration.
        
        Args:
            config: Database configuration. If None, reads from environment.
        """
        self.config = config or DatabaseConfig.from_environment()

    def substitute_template(self, sql_template: str, substitutions: Dict[str, Any]) -> str:
        """Substitute variables in SQL template.
        
        Args:
            sql_template: SQL template with {{variable}} placeholders
            substitutions: Dictionary of variable substitutions
            
        Returns:
            SQL string with variables substituted
            
        Raises:
            SQLTemplateError: If template substitution fails
        """
        try:
            # Find all template variables in format {{variable_name}}
            template_vars = re.findall(r'\{\{(\w+)\}\}', sql_template)
            
            # Check if all required variables are provided
            missing_vars = set(template_vars) - set(substitutions.keys())
            if missing_vars:
                raise SQLTemplateError(f"Missing substitution variables: {missing_vars}")
            
            # Perform substitutions
            result_sql = sql_template
            for var_name, value in substitutions.items():
                placeholder = f"{{{{{var_name}}}}}"
                # Convert value to string and escape single quotes for SQL safety
                if isinstance(value, str):
                    # Escape single quotes by doubling them
                    escaped_value = value.replace("'", "''")
                    result_sql = result_sql.replace(placeholder, escaped_value)
                else:
                    result_sql = result_sql.replace(placeholder, str(value))
            
            return result_sql
            
        except Exception as e:
            raise SQLTemplateError(f"Template substitution failed: {str(e)}") from e

    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL and return results as JSON.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            List of dictionaries representing query results
            
        Raises:
            SQLExecutionError: If SQL execution fails
        """
        try:
            # Create a fresh connection for this query
            db_connection = create_connection(self.config)
            
            with db_connection.get_connection() as connection:
                cursor = connection.cursor()
                
                # Execute the SQL
                cursor.execute(sql)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Fetch all results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        column_name = columns[i] if i < len(columns) else f"column_{i}"
                        # Handle different data types for JSON serialization
                        if isinstance(value, (datetime.datetime, datetime.date)):
                            row_dict[column_name] = value.isoformat()
                        elif value is None:
                            row_dict[column_name] = None
                        else:
                            row_dict[column_name] = value
                    results.append(row_dict)
                
                cursor.close()
                return results
                
        except Exception as e:
            error_msg = f"SQL execution failed: {str(e)}"
            logger.error(error_msg)
            raise SQLExecutionError(error_msg) from e

    def execute_template(self, sql_template: str, substitutions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL template with substitutions and return formatted response.
        
        Args:
            sql_template: SQL template with {{variable}} placeholders
            substitutions: Dictionary of variable substitutions
            
        Returns:
            JSON response with results, metadata, and status
        """
        substitutions = substitutions or {}
        
        try:
            # Substitute template variables
            sql = self.substitute_template(sql_template, substitutions)
            
            # Execute SQL
            results = self.execute_sql(sql)
            
            # Return formatted response
            return {
                "success": True,
                "data": results,
                "row_count": len(results),
                "executed_sql": sql,
                "template": sql_template,
                "substitutions": substitutions,
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                "error": None
            }
            
        except (SQLTemplateError, SQLExecutionError) as e:
            # Return error response
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "executed_sql": None,
                "template": sql_template,
                "substitutions": substitutions,
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                "error": str(e)
            }
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error during template execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "executed_sql": None,
                "template": sql_template,
                "substitutions": substitutions,
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                "error": error_msg
            }


def execute_sql_template(sql_template: str, substitutions: Optional[Dict[str, Any]] = None, 
                        config: Optional[DatabaseConfig] = None) -> Dict[str, Any]:
    """Convenience function to execute SQL template.
    
    Args:
        sql_template: SQL template with {{variable}} placeholders
        substitutions: Dictionary of variable substitutions
        config: Database configuration. If None, reads from environment.
        
    Returns:
        JSON response with results, metadata, and status
    """
    executor = SQLExecutor(config)
    return executor.execute_template(sql_template, substitutions)