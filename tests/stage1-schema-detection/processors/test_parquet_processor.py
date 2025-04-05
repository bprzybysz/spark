"""
Tests for the Parquet processor.
"""

import os
import pytest
import tempfile
import pandas as pd
from datetime import datetime, timedelta

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType

from src.stages.stage1_schema_detection.processors.parquet_processor import ParquetProcessor


@pytest.fixture
def sample_parquet_file(tmp_path, spark_session):
    """Create a sample Parquet file for testing."""
    # Create sample data
    data = [
        (1, datetime.now(), 10.5, "category_A"),
        (2, datetime.now() - timedelta(days=1), 20.0, "category_B"),
        (3, datetime.now() - timedelta(days=2), 30.5, "category_C")
    ]
    
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("timestamp", TimestampType(), True),
        StructField("value", DoubleType(), True),
        StructField("category", StringType(), True)
    ])
    
    df = spark_session.createDataFrame(data, schema=schema)
    
    # Save as parquet
    parquet_path = os.path.join(tmp_path, "sample.parquet")
    df.write.mode("overwrite").parquet(parquet_path)
    
    return parquet_path


def test_parquet_processor_can_process(spark_session, sample_parquet_file):
    """Test Parquet processor can_process method."""
    processor = ParquetProcessor(spark_session)
    
    # Check can_process method
    assert processor.can_process(sample_parquet_file) is True
    assert processor.can_process("not_a_parquet.txt") is False
    assert processor.can_process("file.csv") is False


def test_parquet_processor_schema(spark_session, sample_parquet_file):
    """Test Parquet processor schema extraction."""
    processor = ParquetProcessor(spark_session)
    
    # Extract schema
    schema = processor.extract_schema(sample_parquet_file)
    
    # Verify schema fields
    assert isinstance(schema, StructType)
    assert len(schema.fields) == 4
    
    # Check field names and types
    field_names = [field.name for field in schema.fields]
    assert "id" in field_names
    assert "timestamp" in field_names
    assert "value" in field_names
    assert "category" in field_names
    
    # Verify types
    for field in schema.fields:
        if field.name == "id":
            assert isinstance(field.dataType, IntegerType)
        elif field.name == "timestamp":
            assert field.dataType.typeName() == "timestamp"
        elif field.name == "value":
            assert isinstance(field.dataType, DoubleType)
        elif field.name == "category":
            assert isinstance(field.dataType, StringType)


def test_parquet_processor_validate(spark_session, sample_parquet_file):
    """Test Parquet processor validation."""
    processor = ParquetProcessor(spark_session)
    
    # Validate existing file
    messages = processor.validate(sample_parquet_file)
    assert len(messages) == 0  # No validation errors for a valid file
    
    # Validate non-existent file
    messages = processor.validate("non_existent_file.parquet")
    assert len(messages) == 1
    assert "not found" in messages[0]


def test_parquet_processor_extract_sample_data(spark_session, sample_parquet_file):
    """Test Parquet processor data extraction."""
    processor = ParquetProcessor(spark_session)
    
    # Extract sample data
    sample_data = processor.extract_sample_data(sample_parquet_file, limit=2)
    
    # Verify sample data
    assert sample_data is not None
    assert isinstance(sample_data, DataFrame)
    assert sample_data.count() <= 2  # Should respect the limit
    assert len(sample_data.columns) == 4
    assert sorted(sample_data.columns) == ["category", "id", "timestamp", "value"]


def test_parquet_processor_with_partitions(spark_session, tmp_path):
    """Test Parquet processor with partitioned data."""
    # Create sample partitioned data
    data = []
    for day in range(1, 4):
        for region in ["US", "EU", "ASIA"]:
            for i in range(2):
                data.append((
                    i + day * 10, 
                    f"product_{i}",
                    100.0 * day + i,
                    region,
                    f"2023-01-{day:02d}"
                ))
    
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("region", StringType(), True),
        StructField("date", StringType(), True)
    ])
    
    df = spark_session.createDataFrame(data, schema=schema)
    
    # Save as partitioned parquet
    parquet_path = os.path.join(tmp_path, "partitioned.parquet")
    df.write.mode("overwrite").partitionBy("region", "date").parquet(parquet_path)
    
    processor = ParquetProcessor(spark_session)
    
    # Extract schema
    schema = processor.extract_schema(parquet_path)
    
    # Verify schema contains partition columns
    field_names = [field.name for field in schema.fields]
    assert "id" in field_names
    assert "name" in field_names
    assert "price" in field_names
    assert "region" in field_names  # Partition column
    assert "date" in field_names    # Partition column
    
    # Extract sample data
    sample_data = processor.extract_sample_data(parquet_path)
    
    # Verify sample data contains all columns including partitions
    assert sample_data is not None
    assert len(sample_data.columns) == 5
    assert sorted(sample_data.columns) == ["date", "id", "name", "price", "region"]
    assert sample_data.count() > 0


def test_parquet_processor_schema_evolution(spark_session, tmp_path):
    """Test Parquet processor with schema evolution."""
    # Create initial schema
    schema1 = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("value", DoubleType(), True)
    ])
    
    data1 = [(1, "item1", 10.5), (2, "item2", 20.0)]
    df1 = spark_session.createDataFrame(data1, schema1)
    
    # Save first version
    parquet_path = os.path.join(tmp_path, "evolving.parquet")
    df1.write.mode("overwrite").parquet(parquet_path)
    
    # Create second schema with added column
    schema2 = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("value", DoubleType(), True),
        StructField("category", StringType(), True)
    ])
    
    data2 = [(3, "item3", 30.5, "cat_A"), (4, "item4", 40.0, "cat_B")]
    df2 = spark_session.createDataFrame(data2, schema2)
    
    # Append with new schema
    df2.write.mode("append").parquet(parquet_path)
    
    processor = ParquetProcessor(spark_session)
    
    # Test schema detection with schema evolution
    detected_schema = processor.extract_schema(
        parquet_path, 
        options={"mergeSchema": "true"}
    )
    
    # Verify merged schema contains all fields
    field_names = [field.name for field in detected_schema.fields]
    assert "id" in field_names
    assert "name" in field_names
    assert "value" in field_names
    assert "category" in field_names
    
    # Test sample data with merged schema
    sample_data = processor.extract_sample_data(
        parquet_path,
        options={"mergeSchema": "true"}
    )
    
    # Verify sample data has all columns
    assert "category" in sample_data.columns 


def test_parquet_processor_real_titanic_file(spark_session):
    """Test Parquet processor with a real titanic.parquet file."""
    processor = ParquetProcessor(spark_session)
    titanic_file = "./data/parquet/titanic.parquet"
    
    # Check if processor can handle the file
    assert processor.can_process(titanic_file) is True
    
    # Extract schema
    schema = processor.extract_schema(titanic_file)
    
    # Verify schema fields
    assert isinstance(schema, StructType)
    assert len(schema.fields) == 12  # Titanic dataset has 12 columns
    
    # Check field names and types
    field_names = [field.name for field in schema.fields]
    expected_fields = [
        "PassengerId", "Survived", "Pclass", "Name", "Sex", 
        "Age", "SibSp", "Parch", "Ticket", "Fare", "Cabin", "Embarked"
    ]
    for field in expected_fields:
        assert field in field_names
    
    # Verify specific field types
    for field in schema.fields:
        if field.name == "PassengerId":
            assert field.dataType.typeName() == "long"
        elif field.name == "Name":
            assert field.dataType.typeName() == "string"
        elif field.name == "Age":
            assert field.dataType.typeName() == "double"
    
    # Extract sample data
    sample_data = processor.extract_sample_data(titanic_file, limit=5)
    
    # Verify sample data
    assert sample_data is not None
    assert isinstance(sample_data, DataFrame)
    assert sample_data.count() == 5  # We requested 5 records
    assert len(sample_data.columns) == 12
    
    # Validate the file
    messages = processor.validate(titanic_file)
    assert len(messages) == 0  # No validation errors for a valid file 