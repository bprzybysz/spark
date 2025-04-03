# Testing Guide

This guide outlines the testing practices and standards for the project.

## Testing Philosophy

Our testing approach follows these principles:

1. Tests should be clear and maintainable
2. Each test should have a single responsibility
3. Tests should be independent and isolated
4. Test coverage should be meaningful
5. Tests should serve as documentation

## Test Structure

### Directory Organization

```
tests/
├── stage1_schema/
│   ├── test_schema_detection.py
│   └── test_schema_validation.py
├── stage2_transform/
│   ├── test_data_cleaning.py
│   └── test_transformations.py
├── stage3_quality/
│   ├── test_quality_checks.py
│   └── test_quality_metrics.py
└── stage4_analytics/
    ├── test_aggregations.py
    └── test_analytics.py
```

### File Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Test fixtures: `*_fixture`

## Writing Tests

### Test Function Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_data_transformation():
    """Test data transformation with valid input.
    
    Test scenario:
        Create a DataFrame with sample data and apply transformation
    
    Expected behavior:
        DataFrame should have transformed columns with correct values
    """
    # Arrange
    input_data = [("1", 10), ("2", 20)]
    input_df = spark.createDataFrame(input_data, ["id", "value"])
    
    # Act
    result = transform_data(input_df, ["value"])
    
    # Assert
    assert result.count() == 2, "Row count should remain unchanged"
    assert "transformed_value" in result.columns
```

### Test Documentation

Each test function should have a docstring with:

1. Brief description
2. Test scenario
3. Expected behavior

Example:
```python
def test_schema_validation():
    """Test schema validation with mismatched types.
    
    Test scenario:
        Create a DataFrame with incorrect column types
        and attempt to validate against expected schema
    
    Expected behavior:
        Should raise SchemaValidationError with details
        about the mismatched columns
    """
```

### Fixtures

Use fixtures for common setup:

```python
@pytest.fixture(scope="session")
def spark():
    """Create a SparkSession for testing.
    
    Returns:
        SparkSession configured for testing
    """
    return (SparkSession.builder
            .appName("TestSession")
            .master("local[*]")
            .getOrCreate())

@pytest.fixture
def sample_data(spark):
    """Create sample test data.
    
    Args:
        spark: SparkSession fixture
    
    Returns:
        DataFrame with test data
    """
    data = [
        (1, "A", 10.0),
        (2, "B", 20.0)
    ]
    return spark.createDataFrame(data, ["id", "name", "value"])
```

### Assertions

Follow these guidelines for assertions:

1. Use positive assertions when possible
2. Include descriptive messages
3. Be specific about what's being tested
4. Use appropriate assertion methods

Example:
```python
# Good
assert result.is_valid, "Validation should pass for correct input"
assert len(errors) == 0, "No validation errors should be present"

# Avoid
assert result  # Unclear what's being tested
assert len(errors) != 1  # Negative assertion
```

## Testing PySpark

### DataFrame Testing

1. Create small, focused test datasets
2. Use schema definitions
3. Compare results using DataFrame operations

Example:
```python
def test_aggregation(spark):
    """Test data aggregation functionality."""
    # Create test data
    input_schema = StructType([
        StructField("group", StringType(), True),
        StructField("value", FloatType(), True)
    ])
    
    input_data = [("A", 1.0), ("A", 2.0), ("B", 3.0)]
    input_df = spark.createDataFrame(input_data, input_schema)
    
    # Perform aggregation
    result = aggregate_by_group(input_df, "group", "value")
    
    # Verify results
    expected = {
        "A": 3.0,  # sum of group A
        "B": 3.0   # sum of group B
    }
    
    for row in result.collect():
        assert abs(row.sum - expected[row.group]) < 0.001
```

### Testing Best Practices

1. Clean up SparkSession after tests
2. Use appropriate fixture scopes
3. Handle null values explicitly
4. Test edge cases
5. Verify schema changes

## Test Coverage

### Coverage Requirements

- Minimum coverage: 80%
- Critical paths: 100%
- New code: 90%

### Running Coverage Reports

```bash
poetry run pytest --cov=src tests/
```

### Coverage Exclusions

- Generated code
- External integrations
- Debug/development code

## Continuous Integration

Tests are run automatically on:

1. Pull request creation
2. Push to main branch
3. Release creation

### CI Pipeline

```yaml
test:
  stage: test
  script:
    - poetry install
    - poetry run pytest
    - poetry run pytest --cov=src
  coverage:
    report:
      coverage_report.xml
```

## Troubleshooting Tests

Common issues and solutions:

1. **Spark Context errors**
   - Use `spark_session` fixture
   - Clean up after tests
   - Avoid global state

2. **Inconsistent results**
   - Set random seed
   - Use static test data
   - Avoid time-dependent tests

3. **Slow tests**
   - Use appropriate fixture scopes
   - Minimize data size
   - Parallelize test execution

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [PySpark Testing Guide](https://spark.apache.org/docs/latest/testing.html)
- [Code Coverage Best Practices](https://coverage.readthedocs.io/) 