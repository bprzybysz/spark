"""
Integration tests for Hive with schema detection.
"""

import os
import pytest
import tempfile
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

from src.stages.stage1_schema_detection.detector import SchemaDetector, DataSourceType


@pytest.fixture(scope="module")
def hive_warehouse_dir():
    """Create a temporary Hive warehouse directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="hive_test_warehouse_")
    yield temp_dir
    # Clean up
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def spark_with_hive(hive_warehouse_dir):
    """Create a Spark session with Hive support for testing."""
    # Set up Spark session with Hive support
    spark = (SparkSession.builder
        .appName("HiveIntegrationTest")
        .master("local[2]")
        .config("spark.sql.warehouse.dir", hive_warehouse_dir)
        .config("spark.sql.catalogImplementation", "hive")
        .config("spark.hadoop.javax.jdo.option.ConnectionURL", 
                f"jdbc:derby:;databaseName={hive_warehouse_dir}/metastore_db;create=true")
        .config("spark.hadoop.hive.metastore.schema.verification", "false")
        .enableHiveSupport()
        .getOrCreate())
    
    yield spark
    
    # Clean up
    spark.stop()


@pytest.fixture(scope="module")
def setup_hive_tables(spark_with_hive):
    """Set up Hive tables for testing."""
    spark = spark_with_hive
    
    # Create simple table
    simple_data = [(1, "John", 100.0), (2, "Jane", 200.0), (3, "Bob", 300.0)]
    simple_schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("value", DoubleType(), True)
    ])
    simple_df = spark.createDataFrame(simple_data, schema=simple_schema)
    simple_df.write.mode("overwrite").saveAsTable("simple_test_table")
    
    # Create partitioned table
    partitioned_data = []
    for region in ["US", "EU", "ASIA"]:
        for year in [2021, 2022, 2023]:
            for i in range(3):
                partitioned_data.append((
                    i + 1, 
                    f"product_{i}_{region}_{year}", 
                    i * 10.5 + year, 
                    region, 
                    year
                ))
    
    partitioned_schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("region", StringType(), True),
        StructField("year", IntegerType(), True)
    ])
    
    partitioned_df = spark.createDataFrame(partitioned_data, schema=partitioned_schema)
    partitioned_df.write.mode("overwrite").partitionBy("region", "year").saveAsTable("partitioned_test_table")
    
    # Create table with complex data types
    spark.sql("""
    CREATE TABLE IF NOT EXISTS complex_test_table (
        id INT,
        name STRING,
        tags ARRAY<STRING>,
        properties MAP<STRING, STRING>,
        nested STRUCT<field1: INT, field2: STRING>
    )
    """)
    
    spark.sql("""
    INSERT OVERWRITE TABLE complex_test_table VALUES
    (1, 'Item1', array('tag1', 'tag2'), map('color', 'red', 'size', 'large'), named_struct('field1', 10, 'field2', 'value1')),
    (2, 'Item2', array('tag3', 'tag4'), map('color', 'blue', 'size', 'medium'), named_struct('field1', 20, 'field2', 'value2')),
    (3, 'Item3', array('tag5', 'tag6'), map('color', 'green', 'size', 'small'), named_struct('field1', 30, 'field2', 'value3'))
    """)
    
    yield {
        "simple_table": "simple_test_table",
        "partitioned_table": "partitioned_test_table",
        "complex_table": "complex_test_table",
        "non_existent_table": "non_existent_table"
    }
    
    # Clean up tables after tests
    spark.sql("DROP TABLE IF EXISTS simple_test_table")
    spark.sql("DROP TABLE IF EXISTS partitioned_test_table")
    spark.sql("DROP TABLE IF EXISTS complex_test_table")


def test_hive_simple_table_schema_detection(spark_with_hive, setup_hive_tables):
    """Test schema detection from a simple Hive table."""
    detector = SchemaDetector(spark_with_hive)
    table_name = setup_hive_tables["simple_table"]
    
    # Detect schema
    result = detector.detect_schema(table_name, DataSourceType.HIVE)
    
    # Verify results
    assert result.source_type == DataSourceType.HIVE
    assert result.validation_errors == []
    
    # Check schema
    assert len(result.schema.fields) == 3
    field_names = [field.name for field in result.schema.fields]
    assert "id" in field_names
    assert "name" in field_names
    assert "value" in field_names
    
    # Check sample data
    assert result.sample_data is not None
    assert len(result.sample_data) <= 1000  # Default sample size
    assert list(result.sample_data.columns) == ["id", "name", "value"]


def test_hive_partitioned_table_schema_detection(spark_with_hive, setup_hive_tables):
    """Test schema detection from a partitioned Hive table."""
    detector = SchemaDetector(spark_with_hive)
    table_name = setup_hive_tables["partitioned_table"]
    
    # Detect schema
    result = detector.detect_schema(table_name, DataSourceType.HIVE)
    
    # Verify results
    assert result.source_type == DataSourceType.HIVE
    assert result.validation_errors == []
    
    # Check schema (should include partition columns)
    assert len(result.schema.fields) == 5
    field_names = [field.name for field in result.schema.fields]
    assert "id" in field_names
    assert "name" in field_names
    assert "price" in field_names
    assert "region" in field_names  # Partition column
    assert "year" in field_names    # Partition column
    
    # Check sample data
    assert result.sample_data is not None
    assert len(result.sample_data) <= 1000  # Default sample size


def test_hive_complex_table_schema_detection(spark_with_hive, setup_hive_tables):
    """Test schema detection from a Hive table with complex data types."""
    detector = SchemaDetector(spark_with_hive)
    table_name = setup_hive_tables["complex_table"]
    
    # Detect schema
    result = detector.detect_schema(table_name, DataSourceType.HIVE)
    
    # Verify results
    assert result.source_type == DataSourceType.HIVE
    assert result.validation_errors == []
    
    # Check schema
    assert len(result.schema.fields) == 5
    field_names = [field.name for field in result.schema.fields]
    assert "id" in field_names
    assert "name" in field_names
    assert "tags" in field_names
    assert "properties" in field_names
    assert "nested" in field_names
    
    # Check sample data
    assert result.sample_data is not None
    assert len(result.sample_data) == 3  # All rows


def test_hive_table_not_found(spark_with_hive, setup_hive_tables):
    """Test error handling for non-existent Hive table."""
    detector = SchemaDetector(spark_with_hive)
    table_name = setup_hive_tables["non_existent_table"]
    
    # Detect schema
    result = detector.detect_schema(table_name, DataSourceType.HIVE)
    
    # Verify error handling
    assert result.source_type == DataSourceType.HIVE
    assert len(result.validation_errors) == 1
    assert "Table or view not found" in result.validation_errors[0]
    assert len(result.schema.fields) == 0  # Empty schema


def test_schema_validation_hive(spark_with_hive, setup_hive_tables):
    """Test schema validation for Hive tables."""
    detector = SchemaDetector(spark_with_hive)
    
    # Create a clean table with only numeric data for validation
    numeric_data = [(1, 100.0), (2, 200.0), (3, 300.0)]
    numeric_schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("value", DoubleType(), True)
    ])
    numeric_df = spark_with_hive.createDataFrame(numeric_data, schema=numeric_schema)
    numeric_df.createOrReplaceTempView("numeric_test_table")
    
    # Detect schema from clean numeric table
    result = detector.detect_schema("numeric_test_table", DataSourceType.HIVE)
    
    # Validate schema
    messages = detector.validate_schema(result)
    
    # Verify no validation issues for a clean table with numeric data only
    assert len(messages) == 0
    
    # Clean up
    spark_with_hive.sql("DROP TABLE IF EXISTS numeric_test_table") 