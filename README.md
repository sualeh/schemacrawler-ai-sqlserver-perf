# SchemaCrawler AI MCP Server for SQL Server Performance

This is a Python MCP Server using Fast MCP. Each MCP tool will make a connection to a database, execute SQL and return the results as JSON. The SQL is hardcoded but is a template - parts of the SQL including table names may be replaced based on tool parameters.

## Development

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

4. Run tests:
    ```bash
    # Run all tests with coverage
    poetry run pytest --cov=schemacrawler_ai_sqlserver_perf --cov-report=html
    ```
    ```bash
    # Run specific test file
    poetry run pytest tests/test_version_tool.py -v
    ```

5. Run the server:
    ```bash
    poetry run python -m schemacrawler_ai_sqlserver_perf.main
    ```


## Using Docker

1. Build Docker image locally:
    ```bash
    docker build -t schemacrawler/schemacrawler-ai-sqlserver-perf:latest .
    ```

2. Run Docker container:
    ```bash
    docker run -d -p 8000:8000 schemacrawler/schemacrawler-ai-sqlserver-perf:latest
    ```
