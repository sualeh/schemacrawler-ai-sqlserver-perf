# Column Statistics Tool

The Column Statistics Tool is an MCP (Model Context Protocol) tool that provides detailed column information and statistics for tables in SQL Server databases. This tool is part of the SchemaCrawler AI SQL Server Performance Analysis project.

## Overview

The Column Statistics Tool allows you to analyze table structure and get basic statistical information about columns in a specified table. It provides column metadata from the INFORMATION_SCHEMA and calculates table-level statistics.

## Features

- **Column Metadata**: Retrieves detailed information about each column including data type, nullability, precision, and scale
- **INFORMATION_SCHEMA Format**: Returns database_name, schema_name, and table_name in separate columns following INFORMATION_SCHEMA standards
- **Table Statistics**: Provides total row count for the specified table
- **Extensible Design**: Structured to support future statistical calculations (min/max values, null counts, distinct counts)
- **Error Handling**: Comprehensive error handling for database access issues and invalid table references

## Usage

### Function Signature

```python
async def column_statistics_tool(
    database_name: str, 
    schema_name: str, 
    table_name: str
) -> dict[str, Any]
```

### Parameters

- `database_name` (str): The name of the database containing the table
- `schema_name` (str): The schema name where the table is located
- `table_name` (str): The name of the table to analyze

### Return Format

The tool returns a JSON object with the following structure:

```json
{
    "success": true,
    "message": "Column statistics retrieved successfully for database.schema.table",
    "database_name": "TestDB",
    "schema_name": "dbo", 
    "table_name": "Users",
    "column_count": 3,
    "data": [
        {
            "database_name": "TestDB",
            "schema_name": "dbo",
            "table_name": "Users",
            "COLUMN_NAME": "UserId",
            "DATA_TYPE": "int",
            "IS_NULLABLE": "NO",
            "CHARACTER_MAXIMUM_LENGTH": null,
            "NUMERIC_PRECISION": 10,
            "NUMERIC_SCALE": 0,
            "ORDINAL_POSITION": 1,
            "total_count": 1500,
            "min_value": null,
            "max_value": null,
            "null_count": null,
            "distinct_count": null
        },
        {
            "database_name": "TestDB",
            "schema_name": "dbo",
            "table_name": "Users",
            "COLUMN_NAME": "UserName",
            "DATA_TYPE": "varchar",
            "IS_NULLABLE": "YES",
            "CHARACTER_MAXIMUM_LENGTH": 255,
            "NUMERIC_PRECISION": null,
            "NUMERIC_SCALE": null,
            "ORDINAL_POSITION": 2,
            "total_count": 1500,
            "min_value": null,
            "max_value": null,
            "null_count": null,
            "distinct_count": null
        }
    ]
}
```

### Error Response Format

When an error occurs, the tool returns:

```json
{
    "success": false,
    "message": "Error description",
    "database_name": "TestDB",
    "schema_name": "dbo",
    "table_name": "Users", 
    "column_count": 0,
    "data": [],
    "error": "Detailed error message"
}
```

## Example Usage

### Successful Query

```python
result = await column_statistics_tool("AdventureWorks", "Person", "Contact")

if result["success"]:
    print(f"Found {result['column_count']} columns")
    for column in result["data"]:
        print(f"Column: {column['COLUMN_NAME']} ({column['DATA_TYPE']})")
        print(f"  Nullable: {column['IS_NULLABLE']}")
        print(f"  Total rows: {column['total_count']}")
```

### Error Handling

```python
result = await column_statistics_tool("NonExistent", "dbo", "Table")

if not result["success"]:
    print(f"Error: {result['message']}")
    print(f"Details: {result['error']}")
```

## Column Information Provided

### Basic Metadata
- **COLUMN_NAME**: The name of the column
- **DATA_TYPE**: SQL Server data type (varchar, int, datetime2, etc.)
- **IS_NULLABLE**: Whether the column allows NULL values ("YES" or "NO")
- **ORDINAL_POSITION**: The position of the column in the table definition

### Type-Specific Information
- **CHARACTER_MAXIMUM_LENGTH**: Maximum length for character data types
- **NUMERIC_PRECISION**: Precision for numeric data types
- **NUMERIC_SCALE**: Scale for numeric data types

### Statistical Information
- **total_count**: Total number of rows in the table
- **min_value**: Minimum value in the column (future enhancement)
- **max_value**: Maximum value in the column (future enhancement)
- **null_count**: Count of NULL values in the column (future enhancement)
- **distinct_count**: Count of distinct values in the column (future enhancement)

## Implementation Details

### SQL Template

The tool uses a SQL template that:
1. Queries INFORMATION_SCHEMA.COLUMNS for column metadata
2. Calculates table row count using COUNT(*)
3. Provides structure for future statistical enhancements

### Database Dependencies

- Requires access to INFORMATION_SCHEMA views
- Uses the existing database connection and SQL templating infrastructure
- Follows the same error handling patterns as other database tools

### Performance Considerations

- The current implementation is optimized for metadata retrieval
- Future statistical calculations would require additional optimization for large tables
- Table row count is calculated efficiently using a single COUNT(*) query

## Future Enhancements

The tool is designed to support future statistical calculations:

1. **Min/Max Values**: Calculate actual minimum and maximum values per column
2. **Null Count Analysis**: Count NULL values for each column
3. **Distinct Value Analysis**: Calculate cardinality for each column
4. **Data Distribution**: Histograms and percentile information
5. **Performance Optimization**: Caching and sampling for large tables

## Integration

The Column Statistics Tool is automatically registered with the MCP server when the application starts. It integrates with:

- **Database Connection Module**: Uses existing connection management
- **SQL Executor**: Leverages SQL templating and execution infrastructure
- **Error Handling**: Follows consistent error response patterns
- **Logging**: Integrated with application logging system

## Testing

The tool includes comprehensive test coverage:
- Unit tests with mocked database responses
- Error condition testing
- Edge case handling (special characters, various data types)
- Integration with the existing test infrastructure

## Security Considerations

- Uses parameterized queries through the SQL templating system
- Validates input parameters
- Follows principle of least privilege for database access
- Does not expose sensitive database internals in error messages