"""Hello World MCP tool."""

import datetime
from typing import Any

from pydantic import BaseModel, Field


class VersionInput(BaseModel):
    """Input model for the hello world tool."""

    name: str = Field(description="The name to greet")


async def version_tool() -> dict[str, Any]:
    """
    Shows version of the SchemaCrawler AI MCP Server for
    SQL Server Performance server.

    Returns:
        JSON object with version information
    """
    # Create version message
    message = (
        "SchemaCrawler AI MCP Server for SQL Server Performance."
    )

    # Return JSON response
    return {
        "message": message,
        "timestamp": datetime.datetime.now(datetime.UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "tool": "version",
        "success": True,
    }
