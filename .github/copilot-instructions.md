# SchemaCrawler AI MCP Server for SQL Server Performance

SchemaCrawler AI MCP Server is a Python 3.12+ application that provides an MCP (Model Context Protocol) server for SQL Server performance analysis. The server exposes tools for database connectivity testing and column statistics analysis using FastMCP framework and pyodbc for SQL Server connectivity.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup
- **CRITICAL**: Ensure Python 3.12+ is available: `python3 --version`
- **CRITICAL**: Set Poetry to use Python 3.12: `poetry env use python3.12` -- NEVER SKIP THIS STEP
- Install dependencies: `poetry install` -- takes 30-35 seconds. NEVER CANCEL. Set timeout to 60+ seconds.
- Install test dependencies: `poetry run pip install pytest pytest-cov` -- required for testing, not in main dependencies
- Copy environment template: `cp .env.example .env` -- configure database settings if needed

### Build and Test
- **ALWAYS** run the complete setup sequence above before building or testing
- Compile check: `find schemacrawler_ai_sqlserver_perf -name "*.py" -exec python -m py_compile {} \;` -- takes <5 seconds
- Build package: `poetry build` -- takes <1 second. NEVER CANCEL. Set timeout to 60+ seconds.
- Run all tests: `poetry run pytest --cov=schemacrawler_ai_sqlserver_perf --cov-report=html` -- takes 2-3 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- Run specific test: `poetry run pytest tests/test_sql_executor.py -v` -- takes <1 second
- Quick test run: `poetry run pytest --maxfail=1 --disable-warnings -q` -- takes <2 seconds

### Run the Application
- **ALWAYS** run the bootstrapping steps first
- Start MCP server: `poetry run python -m schemacrawler_ai_sqlserver_perf.main` -- starts immediately and listens on stdio for MCP commands
- The server displays ASCII art banner and waits for MCP protocol messages
- **CRITICAL**: The application runs indefinitely waiting for MCP commands - this is expected behavior

### Code Quality and Linting
- Format code: `poetry run black .` -- takes <1 second. ALWAYS run before committing.
- Check/fix linting: `poetry run ruff check --fix .` -- takes <1 second. ALWAYS run before committing.
- Check formatting only: `poetry run black --check .` -- takes <1 second
- **CRITICAL**: ALWAYS run `poetry run black .` and `poetry run ruff check --fix .` before you are done or the CI (.github/workflows/copilot-setup-steps.yml) will fail

## Validation

### Manual Testing Requirements
- ALWAYS manually validate the MCP server starts correctly by running the main application and verifying the banner displays
- You can build and test the Python application without an actual SQL Server database
- ALWAYS run through the complete build → test → lint cycle after making changes
- Test changes with: `poetry run pytest tests/` to ensure functionality is preserved

### Known Limitations
- **Docker Build**: Currently fails due to SSL certificate issues when downloading Microsoft SQL Server ODBC drivers. Document this as "Docker build fails due to SSL certificate limitations in CI environments"
- **Database Connectivity**: Cannot test actual SQL Server connections without real database credentials
- **One Test Failure**: `test_get_connection_string_sqlserver` fails due to mismatch between expected "Encrypt=yes" and actual "SSLProtocol=TLSv1.2" - this is a test issue, not a functional problem

## Common Tasks

### Repo Root Structure
```
.
├── .github/
│   └── workflows/
│       ├── copilot-setup-steps.yml
│       └── docker.yml
├── schemacrawler_ai_sqlserver_perf/
│   ├── main.py
│   ├── database/
│   └── tools/
├── tests/
├── README.md
├── pyproject.toml
├── Dockerfile
├── .env.example
└── sql-server-performance.md
```

### Key Files Overview
- `schemacrawler_ai_sqlserver_perf/main.py` -- Main entry point for MCP server
- `schemacrawler_ai_sqlserver_perf/tools/database_connection_tool.py` -- Database connectivity tool
- `schemacrawler_ai_sqlserver_perf/database/` -- Database configuration and SQL execution modules
- `tests/` -- Unit tests (pytest-based)
- `pyproject.toml` -- Poetry configuration with Python 3.12+ requirement
- `.env.example` -- Environment variables template for database configuration

### Environment Variables for Database Connection
```
SCHCRWLR_SERVER=sqlserver
SCHCRWLR_HOST=localhost
SCHCRWLR_PORT=1433
SCHCRWLR_DATABASE=master
SCHCRWLR_DATABASE_USER=admin
SCHCRWLR_DATABASE_PASSWORD=p@ssw0rd
```

### Common Command Timing Expectations
- `poetry env use python3.12`: <5 seconds
- `poetry install`: 30-35 seconds - NEVER CANCEL
- `poetry run pytest`: 2-3 seconds - NEVER CANCEL
- `poetry build`: <1 second
- `poetry run black .`: <1 second
- `poetry run ruff check --fix .`: <1 second
- Application startup: immediate (then waits for MCP commands)

### Technology Stack
- Python 3.12+ (required)
- Poetry for dependency management
- FastMCP for MCP server implementation
- pyodbc for SQL Server connectivity
- pytest for testing
- black for code formatting
- ruff for linting
- Docker support (with known SSL issues)

### CI/CD Integration
- GitHub Actions workflows in `.github/workflows/`
- Copilot setup steps validated in `copilot-setup-steps.yml`
- Docker build pipeline in `docker.yml` (currently failing due to SSL certificate issues)
- **CRITICAL**: Always run `poetry run black .` and `poetry run ruff check --fix .` or CI will fail
