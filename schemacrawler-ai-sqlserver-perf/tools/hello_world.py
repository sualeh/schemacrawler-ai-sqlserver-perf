"""Hello World MCP tool."""

import datetime
from typing import Any

from pydantic import BaseModel, Field


class HelloWorldInput(BaseModel):
    """Input model for the hello world tool."""

    name: str = Field(description="The name to greet")


async def hello_world_tool(name: str) -> dict[str, Any]:
    """Greets a user with a personalized hello message.

    Args:
        name: The name to greet

    Returns:
        JSON object with greeting message
    """
    # Create greeting message
    message = (
        f"Hello, {name}! Welcome to SchemaCrawler AI MCP Server "
        "for SQL Server Performance."
    )

    # Return JSON response
    return {
        "message": message,
        "timestamp": datetime.datetime.now(datetime.UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "tool": "hello_world",
        "success": True,
    }
