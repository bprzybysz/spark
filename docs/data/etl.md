# ETL Pipeline

This document describes the Extract, Transform, Load (ETL) pipeline implementation using Apache Spark.

## Spark Session Configuration

The project uses a factory pattern for creating and managing Spark sessions with configurable options:

### Basic Configuration

```python
spark = create_spark_session(
    app_name="SparkETLMLPipeline",
    master="local[*]",
    enable_hive=True,
    enable_arrow=True
)
```

### Configuration Options

- `app_name`: Name of the Spark application
- `master`: Spark master URL (e.g., "local[*]", "yarn", "spark://host:port")
- `config`: Additional Spark configuration options
- `enable_hive`: Enable Hive support for structured data warehousing
- `enable_arrow`: Enable Apache Arrow optimization for Python UDFs

### Performance Optimizations

- Apache Arrow integration for efficient Python UDF execution
- Configurable parallelism through master URL
- Hive metastore integration for structured data management

## Session Management

The `SparkSessionFactory` provides methods for:

- Creating new sessions with custom configurations
- Reusing existing sessions
- Properly stopping and cleaning up sessions

## Best Practices

1. **Resource Management**
   ```python
   # Create session factory
   factory = SparkSessionFactory(app_name="MyApp")
   
   try:
       # Get or create session
       spark = factory.get_session()
       # Perform ETL operations
   finally:
       # Clean up resources
       factory.stop_session()
   ```

2. **Configuration Management**
   - Store configurations in config files
   - Use environment variables for sensitive values
   - Apply appropriate Spark tuning based on data size

3. **Performance Optimization**
   - Enable Arrow for Python UDF optimization
   - Configure appropriate parallelism
   - Use appropriate storage formats (Parquet, ORC)

## ETL Pipeline Structure

1. **Extract**
   - Read from various data sources
   - Apply schema validation
   - Handle data quality issues

2. **Transform**
   - Clean and standardize data
   - Apply business logic
   - Perform feature engineering

3. **Load**
   - Write to target storage
   - Update metadata
   - Validate output

## Integration Points

- Hive Metastore for structured data
- External storage systems
- Machine learning pipeline
- Monitoring and logging systems
