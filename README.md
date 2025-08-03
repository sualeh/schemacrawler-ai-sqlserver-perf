# SchemaCrawler AI MCP Server for SQL Server Performance

This is a Python MCP Server using Fast MCP. Each MCP tool will make a connection to a database, execute SQL and return the results as JSON. The SQL is hardcoded but is a template - parts of the SQL including table names may be replaced based on tool parameters.

## Features

- **Hello World Tool**: A simple MCP tool that greets users with personalized messages
- **Modular Architecture**: Separate modules for tools allowing easy extension
- **Comprehensive Testing**: Unit tests with coverage reporting
- **Docker Support**: Multi-architecture Docker images (AMD64 + ARM64)
- **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions

## Requirements

- Python 3.12+
- Poetry 2.1.3+
- Docker (for containerization)

## Installation

### Using Poetry (Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/sualeh/schemacrawler-ai-sqlserver-perf.git
   cd schemacrawler-ai-sqlserver-perf
   ```

2. Install Poetry if not already installed:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Run the server:
   ```bash
   poetry run python -m schemacrawler_ai.main
   ```

### Using Docker

```bash
docker run -p 8000:8000 schemacrawler-ai/sqlserver-perf:latest
```

## Development

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=schemacrawler_ai --cov-report=html

# Run specific test file
poetry run pytest tests/test_version.py -v
```

### Code Quality

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy schemacrawler_ai/ --ignore-missing-imports
```

### Project Structure

```
schemacrawler-ai-sqlserver-perf/
├── schemacrawler_ai/           # Main package
│   ├── __init__.py
│   ├── main.py                 # MCP server entry point
│   └── tools/                  # MCP tools module
│       ├── __init__.py
│       └── version.py      # Hello World tool
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_version.py
│   └── test_main.py
├── pyproject.toml              # Poetry configuration
├── Dockerfile                  # Docker configuration
└── .github/workflows/          # CI/CD pipeline
    └── ci-cd.yml
```

## MCP Tools

### Hello World Tool

The `version` tool demonstrates basic MCP functionality:

- **Input**: `name` (string) - The name to greet
- **Output**: JSON object with greeting message, timestamp, and success status

Example usage through MCP protocol:
```json
{
  "name": "Alice"
}
```

Returns:
```json
{
  "message": "Hello, Alice! Welcome to SchemaCrawler AI MCP Server for SQL Server Performance.",
  "timestamp": "2025-01-03T13:24:00Z",
  "tool": "version",
  "success": true
}
```

## Adding New Tools

1. Create a new tool module in `schemacrawler_ai/tools/`
2. Implement the tool function with proper type annotations
3. Register the tool in `schemacrawler_ai/main.py`
4. Add tests in the `tests/` directory

Example tool structure:
```python
async def my_new_tool(param: str) -> dict[str, Any]:
    """Description of the tool.

    Args:
        param: Description of the parameter

    Returns:
        JSON object with tool results
    """
    return {"result": f"Processed {param}"}
```

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline that:

1. **Tests**: Runs unit tests, linting, and type checking
2. **Build**: Creates multi-architecture Docker images
3. **Deploy**: Pushes images to Docker Hub
4. **Integration Test**: Validates deployed images

The pipeline runs on:
- Pull requests (test only)
- Pushes to main/develop branches (full pipeline)

## License

This project is part of the SchemaCrawler ecosystem.
