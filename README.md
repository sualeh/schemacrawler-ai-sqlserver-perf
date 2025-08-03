# SchemaCrawler AI MCP Server for SQL Server Performance

This is a Python MCP Server using Fast MCP. Each MCP tool will make a connection to a database, execute SQL and return the results as JSON. The SQL is hardcoded but is a template - parts of the SQL including table names may be replaced based on tool parameters.

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
   poetry run python -m schemacrawler_ai_sqlserver_perf.main
   ```

### Using Docker

#### Build Docker Image Locally

```bash
docker build -t schemacrawler/schemacrawler-ai-sqlserver-perf:latest .
```

#### Run Docker Image

```bash
docker run -d -p 8000:8000 schemacrawler/schemacrawler-ai-sqlserver-perf:latest
```


## Development

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=schemacrawler_ai_sqlserver_perf --cov-report=html

# Run specific test file
poetry run pytest tests/test_version_tool.py -v
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

## License

This project is part of the SchemaCrawler ecosystem.
