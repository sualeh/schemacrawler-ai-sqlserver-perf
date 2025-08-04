# Database Connection Module

This module provides database connection functionality for the SchemaCrawler AI SQL Server Performance Analysis project.

## Features

- **Multiple Connection Methods**: Support for both JDBC URL and individual parameter configuration
- **Environment Variable Configuration**: Easy deployment through environment variables
- **SQL Server Support**: Optimized for Microsoft SQL Server on Linux and Windows 11
- **Connection Validation**: Automatic connection validation on server startup
- **Extensible Design**: Built to support future database platforms (Oracle, IBM DB2, PostgreSQL, MySQL, SQLite)
- **Context Managers**: Safe connection handling with automatic cleanup
- **Comprehensive Testing**: 95%+ test coverage with extensive unit and integration tests

## Environment Variables

### Option 1: JDBC URL Connection

```bash
export SCHCRWLR_JDBC_URL="jdbc:sqlserver://localhost:1433;databaseName=mydb"
export SCHCRWLR_DATABASE_USER="myuser"
export SCHCRWLR_DATABASE_PASSWORD="mypassword"
```

### Option 2: Individual Parameters

```bash
export SCHCRWLR_SERVER="sqlserver"
export SCHCRWLR_HOST="localhost"
export SCHCRWLR_PORT="1433"
export SCHCRWLR_DATABASE="mydb"
export SCHCRWLR_DATABASE_USER="myuser"
export SCHCRWLR_DATABASE_PASSWORD="mypassword"
```

## Usage Examples

### Basic Connection

```python
from schemacrawler_ai_sqlserver_perf.database import create_connection

# Create connection from environment variables
connection = create_connection()

# Validate connection
if connection.validate_connection():
    print("Connection successful!")
else:
    print("Connection failed!")
```

### Using Context Manager

```python
from schemacrawler_ai_sqlserver_perf.database import create_connection

connection = create_connection()

# Use with context manager for automatic cleanup
with connection.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    result = cursor.fetchone()
    print(f"SQL Server Version: {result[0]}")
```

### Manual Configuration

```python
from schemacrawler_ai_sqlserver_perf.database import DatabaseConfig, DatabaseConnection

# Create configuration manually
config = DatabaseConfig(
    server="sqlserver",
    host="localhost",
    port=1433,
    database="mydb",
    username="myuser",
    password="mypassword"
)

# Create connection with custom config
connection = DatabaseConnection(config)
```

## Dependencies

The module requires the following dependencies:

- **pyodbc**: SQL Server ODBC driver for Python
- **pydantic**: Configuration validation and parsing

These are automatically installed with the package.

## SQL Server Driver Requirements

The module uses ODBC Driver 17 for SQL Server. On most systems, this should be available, but you may need to install it:

### Windows
Download and install from Microsoft's official website.

### Linux (Ubuntu/Debian)
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### Linux (Red Hat/CentOS)
```bash
curl https://packages.microsoft.com/config/rhel/8/prod.repo > /etc/yum.repos.d/mssql-release.repo
yum remove unixODBC-utf16 unixODBC-utf16-devel
ACCEPT_EULA=Y yum install -y msodbcsql17
```

## Connection String Details

The module generates connection strings with the following security settings:
- `Encrypt=yes`: Enables SSL encryption
- `TrustServerCertificate=yes`: Allows self-signed certificates (development)

For production environments, you may want to configure proper SSL certificates.

## Error Handling

The module provides comprehensive error handling:

- **Missing Credentials**: Clear error messages for missing username/password
- **Invalid Configuration**: Validation errors for malformed JDBC URLs or missing parameters
- **Connection Failures**: Proper exception handling for database connection issues
- **Driver Issues**: Clear error messages when pyodbc is not available

## Testing

Run the test suite:

```bash
# Run all database tests
pytest tests/test_database_config.py tests/test_database_connection.py -v

# Run with coverage
pytest tests/ --cov=schemacrawler_ai_sqlserver_perf.database --cov-report=term-missing
```

## Server Integration

The database connection is automatically validated when the MCP server starts. If the connection fails, the server will terminate with an error code, ensuring that the application doesn't run without proper database connectivity.

## Future Extensibility

The module is designed to support additional database types. To add support for a new database:

1. Add the database type to the `validate_server` method in `DatabaseConfig`
2. Implement connection string generation in `get_connection_string`
3. Add appropriate JDBC URL parsing logic in `_parse_jdbc_url`
4. Install the necessary database drivers
5. Add comprehensive tests for the new database type

Currently planned for future support:
- Oracle Database
- IBM DB2
- PostgreSQL
- MySQL
- SQLite