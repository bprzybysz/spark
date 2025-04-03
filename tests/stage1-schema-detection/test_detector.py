"""Tests for the schema detection implementation."""

import json
from pathlib import Path
import pytest
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
)
from datetime import datetime

from src.utility.base import StageStatus
from src.stages.stage1_schema_detection.detector import (
    SchemaDetector,
    SchemaDetectionStage,
    DataSourceType,
    SchemaDetectionResult
)

@pytest.fixture(scope="session")
def spark():
    """Fixture providing a SparkSession for testing.
    
    Returns:
        Active SparkSession instance
    """
    return (SparkSession.builder
            .appName("schema-detection-test")
            .master("local[1]")
            .getOrCreate())

@pytest.fixture
def detector(spark):
    """Fixture providing a SchemaDetector instance.
    
    Args:
        spark: SparkSession fixture
        
    Returns:
        SchemaDetector instance
    """
    return SchemaDetector(spark)

@pytest.fixture
def stage(spark):
    """Fixture providing a SchemaDetectionStage instance.
    
    Args:
        spark: SparkSession fixture
        
    Returns:
        SchemaDetectionStage instance
    """
    return SchemaDetectionStage(spark)

@pytest.fixture
def test_data_files(test_data_dir, spark):
    """Fixture creating test data files.
    
    Args:
        test_data_dir: Test data directory fixture
        spark: SparkSession fixture
        
    Returns:
        Dict mapping file types to their paths
    """
    # Create CSV test data
    csv_data = pd.DataFrame({
        'id': range(1, 6),
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'score': [95.5, 87.0, None, 92.5, 88.0]
    })
    csv_path = test_data_dir / "test.csv"
    csv_data.to_csv(csv_path, index=False)
    
    # Create JSON test data
    json_data = [
        {'id': 1, 'name': 'Alice', 'tags': ['a', 'b']},
        {'id': 2, 'name': 'Bob', 'tags': ['c']},
        {'id': 3, 'name': None, 'tags': []}
    ]
    json_path = test_data_dir / "test.json"
    with open(json_path, 'w') as f:
        for record in json_data:
            f.write(json.dumps(record) + '\n')
            
    # Create Parquet test data using PySpark
    parquet_schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("value", DoubleType(), True),
        StructField("category", StringType(), True)
    ])
    
    parquet_data = [
        (1, datetime(2024, 1, 1, 0, 0, 0), 1.5, "A"),
        (2, datetime(2024, 1, 1, 1, 0, 0), None, "B"),
        (3, datetime(2024, 1, 1, 2, 0, 0), 3.5, "A")
    ]
    
    parquet_df = spark.createDataFrame(parquet_data, schema=parquet_schema)
    parquet_path = test_data_dir / "test.parquet"
    parquet_df.write.mode("overwrite").parquet(str(parquet_path))
            
    # Create invalid CSV files
    invalid_csv = test_data_dir / "invalid.csv"
    invalid_csv.write_text("a,b,c\n1,2\n3,4,5,6")  # Inconsistent columns
    
    empty_csv = test_data_dir / "empty.csv"
    empty_csv.write_text("")  # Empty file
    
    return {
        'csv': csv_path,
        'json': json_path,
        'parquet': parquet_path,
        'invalid_csv': invalid_csv,
        'empty_csv': empty_csv
    }

class TestSchemaDetectionStage:
    """Test suite for SchemaDetectionStage class."""
    
    def test_stage_initialization(self, stage):
        """Test stage initialization."""
        assert stage.name == "schema_detection"
        assert stage.config == {}
    
    def test_config_validation(self, stage):
        """Test configuration validation."""
        # Test with empty config
        errors = stage.validate_config()
        assert len(errors) == 2
        assert "source_path" in errors[0]
        assert "source_type" in errors[1]
        
        # Test with valid config
        stage.config = {
            'source_path': 'test.csv',
            'source_type': 'csv'
        }
        assert len(stage.validate_config()) == 0
    
    def test_stage_execution(self, stage, test_data_files):
        """Test stage execution with valid input."""
        # Configure stage
        stage.config = {
            'source_path': str(test_data_files['csv']),
            'source_type': 'csv'
        }
        
        # Execute stage
        result = stage.execute()
        
        assert result.status == StageStatus.COMPLETED
        assert result.stage_name == "schema_detection"
        assert isinstance(result.output, SchemaDetectionResult)
        assert result.output.source_type == DataSourceType.CSV
        assert len(result.output.schema.fields) == 3
    
    def test_stage_execution_failure(self, stage):
        """Test stage execution with invalid input."""
        # Configure stage with non-existent file
        stage.config = {
            'source_path': 'nonexistent.csv',
            'source_type': 'csv'
        }
        
        # Execute stage
        result = stage.execute()
        
        assert result.status == StageStatus.FAILED
        assert len(result.errors) > 0

class TestSchemaDetector:
    """Test suite for SchemaDetector class."""
    
    def test_infer_source_type(self, detector):
        """Test source type inference from file paths."""
        assert detector._infer_source_type("data.csv") == DataSourceType.CSV
        assert detector._infer_source_type("data.json") == DataSourceType.JSON
        assert detector._infer_source_type("data.parquet") == DataSourceType.PARQUET
        assert detector._infer_source_type("my_table") == DataSourceType.HIVE
        
        with pytest.raises(ValueError):
            detector._infer_source_type("unknown.xyz")
    
    def test_detect_csv_schema(self, detector, test_data_files):
        """Test schema detection from CSV file."""
        result = detector.detect_schema(test_data_files['csv'])
        
        assert result.source_type == DataSourceType.CSV
        assert isinstance(result.schema, StructType)
        assert len(result.schema.fields) == 3
        
        # Verify column names and types
        assert result.schema.fields[0].name == "id"
        assert isinstance(result.schema.fields[0].dataType, IntegerType)
        
        assert result.schema.fields[1].name == "name"
        assert isinstance(result.schema.fields[1].dataType, StringType)
        
        assert result.schema.fields[2].name == "score"
        assert isinstance(result.schema.fields[2].dataType, DoubleType)
        
        # Verify sample data
        assert result.sample_data is not None
        assert len(result.sample_data) == 5
        assert list(result.sample_data.columns) == ["id", "name", "score"]
    
    def test_detect_json_schema(self, detector, test_data_files):
        """Test schema detection from JSON file."""
        result = detector.detect_schema(test_data_files['json'])
        
        assert result.source_type == DataSourceType.JSON
        assert isinstance(result.schema, StructType)
        assert len(result.schema.fields) == 3
        
        # Verify sample data
        assert result.sample_data is not None
        assert len(result.sample_data) == 3
        assert list(result.sample_data.columns) == ["id", "name", "tags"]
    
    def test_schema_validation(self, detector, test_data_files):
        """Test schema validation functionality."""
        # Test CSV with null values
        result = detector.detect_schema(test_data_files['csv'])
        messages = detector.validate_schema(result)
        
        # Should detect null values in 'score' column
        assert any("score" in msg and "null values" in msg for msg in messages)
        
        # Test JSON with mixed types
        result = detector.detect_schema(test_data_files['json'])
        messages = detector.validate_schema(result)
        
        # Should detect object type for 'tags' column
        assert any("tags" in msg and "object" in msg for msg in messages)
    
    def test_error_handling(self, detector, test_data_files):
        """Test error handling for invalid inputs."""
        # Test with non-existent file
        result = detector.detect_schema(test_data_files['csv'].parent / "nonexistent.csv")
        assert len(result.validation_errors) > 0
        assert result.schema == StructType([])
        
        # Test with invalid CSV format
        result = detector.detect_schema(test_data_files['invalid_csv'])
        assert len(result.validation_errors) > 0
        assert "Inconsistent number of columns" in result.validation_errors[0]
        
        # Test with empty CSV file
        result = detector.detect_schema(test_data_files['empty_csv'])
        assert len(result.validation_errors) > 0
        assert "Empty CSV file" in result.validation_errors[0]
    
    def test_detect_parquet_schema(self, detector, test_data_files):
        """Test schema detection from Parquet file."""
        result = detector.detect_schema(test_data_files['parquet'])
        
        assert result.source_type == DataSourceType.PARQUET
        assert isinstance(result.schema, StructType)
        assert len(result.schema.fields) == 4
        
        # Verify column names and types
        assert result.schema.fields[0].name == "id"
        assert isinstance(result.schema.fields[0].dataType, IntegerType)
        
        assert result.schema.fields[1].name == "timestamp"
        assert result.schema.fields[1].dataType.typeName() == "timestamp"
        
        assert result.schema.fields[2].name == "value"
        assert isinstance(result.schema.fields[2].dataType, DoubleType)
        
        assert result.schema.fields[3].name == "category"
        assert isinstance(result.schema.fields[3].dataType, StringType)
        
        # Verify sample data
        assert result.sample_data is not None
        assert len(result.sample_data) == 3
        assert list(result.sample_data.columns) == ["id", "timestamp", "value", "category"]
    
    def test_detect_hive_schema(self, detector, spark):
        """Test schema detection from Hive table."""
        # Create a temporary Hive table for testing with explicit schema
        test_data = [(1, "test1", 10.5), (2, "test2", 20.0)]
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", DoubleType(), True)
        ])
        test_df = spark.createDataFrame(test_data, schema)
        test_df.createOrReplaceTempView("test_hive_table")

        result = detector.detect_schema("test_hive_table", DataSourceType.HIVE)

        assert result.source_type == DataSourceType.HIVE
        assert isinstance(result.schema, StructType)
        assert len(result.schema.fields) == 3

        # Verify column names and types
        assert result.schema.fields[0].name == "id"
        assert isinstance(result.schema.fields[0].dataType, IntegerType)
        assert result.schema.fields[1].name == "name"
        assert isinstance(result.schema.fields[1].dataType, StringType)
        assert result.schema.fields[2].name == "value"
        assert isinstance(result.schema.fields[2].dataType, DoubleType)

        # Verify sample data
        assert result.sample_data is not None
        assert len(result.sample_data) == 2
        assert list(result.sample_data.columns) == ["id", "name", "value"]
    
    def test_hive_table_not_found(self, detector):
        """Test error handling for non-existent Hive table."""
        result = detector.detect_schema("nonexistent_table", DataSourceType.HIVE)
        
        assert result.source_type == DataSourceType.HIVE
        assert len(result.schema.fields) == 0  # Empty schema
        assert len(result.validation_errors) == 1
        assert "Table or view not found" in result.validation_errors[0]
    
    def test_parquet_file_not_found(self, detector):
        """Test error handling for non-existent Parquet file."""
        result = detector.detect_schema("nonexistent.parquet", DataSourceType.PARQUET)
        
        assert result.source_type == DataSourceType.PARQUET
        assert len(result.schema.fields) == 0  # Empty schema
        assert len(result.validation_errors) == 1
        assert "File not found" in result.validation_errors[0] 