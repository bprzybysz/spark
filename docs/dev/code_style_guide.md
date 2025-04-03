# Code Style Guide

This document outlines the coding standards and style guidelines for the project.

## Python Code Style

### General Guidelines

- Line length: 100 characters maximum
- Indentation: 4 spaces
- Quote style: Double quotes for strings
- Docstring style: Google format
- Type hints: Required for function arguments and return types

### Import Style

Imports should be organized in the following sections:

1. Future imports
2. Standard library imports
3. Third-party imports
4. First-party imports
5. Local folder imports

Example:
```python
from __future__ import annotations

import os
from typing import List, Optional

import pyspark
from pyspark.sql import DataFrame, SparkSession

from src.core.config import Config
from src.utils.spark import create_spark_session

from .helpers import process_data
```

### Naming Conventions

- Classes: `PascalCase`
- Functions: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_CASE`
- Parameters: `snake_case`
- Test fixtures: `snake_case`

### PySpark Specific

- Builder pattern should use multiline format
- Prefer method chaining (max 4 operations)
- DataFrame operations should be clear and well-documented

Example:
```python
spark = (SparkSession.builder
         .appName("MyApp")
         .master("local[*]")
         .getOrCreate())

df = (spark.read
      .format("parquet")
      .option("header", "true")
      .load("path/to/data"))
```

## Documentation

### Class Documentation

Required sections:
- Attributes
- Methods
- Examples

Example:
```python
class DataProcessor:
    """Process data using Spark transformations.
    
    Attributes:
        spark: SparkSession instance
        config: Configuration object
    
    Methods:
        process_data: Apply transformations to input DataFrame
        validate_schema: Ensure DataFrame matches expected schema
    
    Examples:
        >>> processor = DataProcessor(spark, config)
        >>> result = processor.process_data(input_df)
    """
```

### Function Documentation

Required sections:
- Args
- Returns
- Raises

Example:
```python
def transform_data(
    df: DataFrame,
    columns: List[str]
) -> DataFrame:
    """Transform specified columns in the DataFrame.
    
    Args:
        df: Input DataFrame to transform
        columns: List of column names to process
    
    Returns:
        DataFrame with transformed columns
    
    Raises:
        ValueError: If specified columns don't exist
    """
```

## Testing

### Test Structure

- Test files: Named `test_*.py`
- Test functions: Named `test_*`
- Fixture functions: Named `*_fixture`
- Maximum test size: 50 lines
- Follow Arrange-Act-Assert pattern

### Test Documentation

Required sections:
- Test scenario
- Expected behavior

Example:
```python
def test_data_transformation():
    """Test data transformation with valid input.
    
    Test scenario:
        Create a DataFrame with sample data and apply transformation
    
    Expected behavior:
        DataFrame should have transformed columns with correct values
    """
```

### Assertions

- Prefer positive assertions
- Include descriptive messages
- Use direct boolean style
- Each test should focus on one concept

Example:
```python
def test_validation():
    result = validate_data(df)
    assert result.is_valid, "Data validation should pass for valid input"
    assert len(result.errors) == 0, "No validation errors should be present"
```

## Git Workflow

### Commit Messages

Format: `type(scope): description`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding or modifying tests
- chore: Maintenance tasks
- perf: Performance improvements

Example:
```
feat(data-processing): add support for CSV input files
```

### Branch Naming

Pattern: `^(feature|bugfix|hotfix|release)/[a-z0-9-]+$`
Maximum length: 50 characters

Examples:
- `feature/add-csv-support`
- `bugfix/fix-null-handling`
- `hotfix/security-patch`
- `release/v1.2.0` 