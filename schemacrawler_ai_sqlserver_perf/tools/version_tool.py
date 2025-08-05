"""Version MCP tool."""

import datetime
import importlib.metadata
from typing import Any


def get_package_version() -> str:
    """Get the package version from metadata."""
    try:
        return importlib.metadata.version("schemacrawler_ai_sqlserver_perf")
    except Exception:
        # Fallback to reading from pyproject.toml if package not installed or other error occurs
        try:
            import tomllib
            import pathlib
            
            # Get the project root directory (3 levels up from this file)
            project_root = pathlib.Path(__file__).parent.parent.parent
            pyproject_path = project_root / "pyproject.toml"
            
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "Unknown")
        except Exception:
            pass
        return "Unknown"


async def version_tool() -> dict[str, Any]:
    """
    Shows version of the SchemaCrawler AI MCP Server for
    SQL Server Performance server.

    Returns:
        JSON object with version information
    """
    # Get package version
    version = get_package_version()
    
    # Create version message
    server_name = "SchemaCrawler AI MCP Server for SQL Server Performance"
    message = f"{server_name} version {version}."

    # Return JSON response
    return {
        "message": message,
        "server_name": server_name,
        "version": version,
        "timestamp": datetime.datetime.now(datetime.UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "tool": "version",
        "success": True,
    }
