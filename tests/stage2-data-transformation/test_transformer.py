"""Tests for the data transformation implementation."""

import json
from pathlib import Path
import pytest
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, TimestampType, BooleanType
)
from datetime import datetime

from src.utility.base import StageStatus
from src.stages.stage2_data_transformation.transformer import (
    DataTransformer,
    DataTransformationStage,
    TransformationType,
    TransformationResult,
    DataQualityMetrics
)

@pytest.fixture(scope="session")
def spark():
    """Fixture providing a SparkSession for testing.
    
    Returns:
        Active SparkSession instance
    """
    return (SparkSession.builder
            .appName("data-transformation-test")
            .master("local[1]")
            .getOrCreate())

@pytest.fixture
def transformer(spark):
    """Fixture providing a DataTransformer instance.
    
    Args:
        spark: SparkSession fixture
        
    Returns:
        DataTransformer instance
    """
    return DataTransformer(spark)

@pytest.fixture
def stage(spark):
    """Fixture providing a DataTransformationStage instance.
    
    Args:
        spark: SparkSession fixture
        
    Returns:
        DataTransformationStage instance
    """
    return DataTransformationStage(spark)

@pytest.fixture
def test_data_files(test_data_dir, spark):
    """Fixture creating test data files.
    
    Args:
        test_data_dir: Test data directory fixture
        spark: SparkSession fixture
        
    Returns:
        Dict mapping file types to their paths
    """
    # Create test data with various types and quality issues
    data = [
        {
            'id': 1,
            'name': ' Alice ',  # Whitespace to clean
            'score': 95.5678,  # Decimal to round
            'timestamp': '2024-01-01 00:00:00',
            'active': 'true',  # String to convert to boolean
            'category': 'A'
        },
        {
            'id': 2,
            'name': None,  # Null value
            'score': None,  # Null value
            'timestamp': '2024-01-01 01:00:00',
            'active': 'false',
            'category': 'B'
        },
        {
            'id': 2,  # Duplicate ID
            'name': 'Charlie',
            'score': 150.0,  # Out of range
            'timestamp': 'invalid',  # Invalid timestamp
            'active': 'invalid',  # Invalid boolean
            'category': 'A'
        }
    ]
    
    # Create CSV test data
    csv_data = pd.DataFrame(data)
    csv_path = test_data_dir / "test.csv"
    csv_data.to_csv(csv_path, index=False)
    
    # Create JSON test data
    json_path = test_data_dir / "test.json"
    with open(json_path, 'w') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')
    
    # Create Parquet test data
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("score", DoubleType(), True),
        StructField("timestamp", StringType(), True),
        StructField("active", StringType(), True),
        StructField("category", StringType(), True)
    ])
    
    df = spark.createDataFrame(data, schema)
    parquet_path = test_data_dir / "test.parquet"
    df.write.mode("overwrite").parquet(str(parquet_path))
    
    return {
        'csv': csv_path,
        'json': json_path,
        'parquet': parquet_path
    }

class TestDataTransformationStage:
    """Test suite for DataTransformationStage class."""
    
    def test_stage_initialization(self, stage):
        """Test stage initialization."""
        assert stage.name == "data_transformation"
        assert stage.config == {}
    
    def test_config_validation(self, stage):
        """Test configuration validation."""
        # Test with empty config
        errors = stage.validate_config()
        assert len(errors) == 3
        assert "input_path" in errors[0]
        assert "output_path" in errors[1]
        assert "transformations" in errors[2]
        
        # Test with invalid transformation type
        stage.config = {
            'input_path': 'test.csv',
            'output_path': 'output.csv',
            'transformations': [
                {'type': 'invalid_type'}
            ]
        }
        errors = stage.validate_config()
        assert len(errors) == 1
        assert "Invalid transformation type" in errors[0]
        
        # Test with valid config
        stage.config = {
            'input_path': 'test.csv',
            'output_path': 'output.csv',
            'transformations': [
                {'type': 'clean', 'columns': ['name']}
            ]
        }
        assert len(stage.validate_config()) == 0
    
    def test_stage_execution(self, stage, test_data_files):
        """Test stage execution with valid input."""
        # Configure stage
        stage.config = {
            'input_path': str(test_data_files['csv']),
            'output_path': str(test_data_files['csv'].parent / "output.csv"),
            'transformations': [
                {
                    'type': 'clean',
                    'columns': ['name'],
                    'options': {'remove_whitespace': True}
                }
            ]
        }
        
        # Execute stage
        result = stage.execute()
        
        assert result.status == StageStatus.COMPLETED
        assert result.stage_name == "data_transformation"
        assert isinstance(result.output, TransformationResult)
        assert result.output.transformed_data is not None
    
    def test_stage_execution_failure(self, stage):
        """Test stage execution with invalid input."""
        # Configure stage with non-existent file
        stage.config = {
            'input_path': 'nonexistent.csv',
            'output_path': 'output.csv',
            'transformations': []
        }
        
        # Execute stage
        result = stage.execute()
        
        assert result.status == StageStatus.FAILED
        assert len(result.errors) > 0

class TestDataTransformer:
    """Test suite for DataTransformer class."""
    
    def test_clean_data(self, transformer, test_data_files, spark):
        """Test data cleaning transformation."""
        # Load test data
        df = spark.read.csv(str(test_data_files['csv']), header=True, inferSchema=True)
        
        # Apply cleaning transformation
        result = transformer.transform_data(
            df,
            df.schema,
            [
                {
                    'type': 'clean',
                    'columns': ['name'],
                    'options': {
                        'remove_whitespace': True,
                        'replace_nulls': 'UNKNOWN'
                    }
                }
            ]
        )
        
        # Verify results
        transformed_df = result.transformed_data
        assert transformed_df is not None
        
        # Check whitespace removal
        name_values = [row.name for row in transformed_df.collect()]
        assert 'Alice' in name_values  # Whitespace removed
        assert 'UNKNOWN' in name_values  # Null replaced
    
    def test_convert_types(self, transformer, test_data_files, spark):
        """Test type conversion transformation."""
        df = spark.read.csv(str(test_data_files['csv']), header=True, inferSchema=True)
        
        result = transformer.transform_data(
            df,
            df.schema,
            [
                {
                    'type': 'convert',
                    'type_mappings': {
                        'timestamp': 'timestamp',
                        'active': 'boolean',
                        'score': 'double'
                    },
                    'options': {
                        'timestamp_format': 'yyyy-MM-dd HH:mm:ss'
                    }
                }
            ]
        )
        
        transformed_df = result.transformed_data
        assert transformed_df is not None
        
        # Verify type conversions
        schema = transformed_df.schema
        assert isinstance(schema['timestamp'].dataType, TimestampType)
        assert isinstance(schema['active'].dataType, BooleanType)
        assert isinstance(schema['score'].dataType, DoubleType)
    
    def test_format_data(self, transformer, test_data_files, spark):
        """Test data formatting transformation."""
        df = spark.read.csv(str(test_data_files['csv']), header=True, inferSchema=True)
        
        result = transformer.transform_data(
            df,
            df.schema,
            [
                {
                    'type': 'format',
                    'format_specs': {
                        'category': {'case': 'upper'},
                        'score': {'decimal_places': 2}
                    }
                }
            ]
        )
        
        transformed_df = result.transformed_data
        assert transformed_df is not None
        
        # Verify formatting
        data = transformed_df.collect()
        categories = [row.category for row in data]
        assert all(cat in ['A', 'B'] for cat in categories)
        
        scores = [row.score for row in data if row.score is not None]
        assert all(str(score).split('.')[-1] in ['0', '00', '50', '57'] for score in scores)
    
    def test_validate_data(self, transformer, test_data_files, spark):
        """Test data validation."""
        df = spark.read.csv(str(test_data_files['csv']), header=True, inferSchema=True)
        
        result = transformer.transform_data(
            df,
            df.schema,
            [
                {
                    'type': 'validate',
                    'rules': [
                        {'column': 'id', 'type': 'unique'},
                        {'column': 'name', 'type': 'not_null'},
                        {
                            'column': 'score',
                            'type': 'range',
                            'min': 0,
                            'max': 100
                        }
                    ]
                }
            ]
        )
        
        # Verify validation results
        assert result.quality_metrics is not None
        assert len(result.quality_metrics.validation_errors) > 0
        
        # Check specific validations
        errors = result.quality_metrics.validation_errors
        assert any('duplicate' in err for err in errors)  # Duplicate ID
        assert any('null values' in err for err in errors)  # Null name
        assert any('outside range' in err for err in errors)  # Score > 100
    
    def test_custom_transformation(self, transformer, test_data_files, spark):
        """Test custom transformation function."""
        df = spark.read.csv(str(test_data_files['csv']), header=True, inferSchema=True)
        
        def custom_transform(df, prefix=""):
            """Example custom transformation."""
            from pyspark.sql.functions import concat, lit
            return df.withColumn(
                'name',
                concat(lit(prefix), df.name)
            )
        
        result = transformer.transform_data(
            df,
            df.schema,
            [
                {
                    'type': 'custom',
                    'function': custom_transform,
                    'args': {'prefix': 'User_'}
                }
            ]
        )
        
        transformed_df = result.transformed_data
        assert transformed_df is not None
        
        # Verify custom transformation
        names = [row.name for row in transformed_df.collect() if row.name is not None]
        assert all(name.startswith('User_') for name in names)
    
    def test_transformation_chain(self, transformer, test_data_files, spark):
        """Test chaining multiple transformations."""
        df = spark.read.csv(str(test_data_files['csv']), header=True, inferSchema=True)
        
        result = transformer.transform_data(
            df,
            df.schema,
            [
                # Clean data first
                {
                    'type': 'clean',
                    'columns': ['name'],
                    'options': {
                        'remove_whitespace': True,
                        'replace_nulls': 'UNKNOWN'
                    }
                },
                # Then convert types
                {
                    'type': 'convert',
                    'type_mappings': {
                        'score': 'double',
                        'active': 'boolean'
                    }
                },
                # Format the data
                {
                    'type': 'format',
                    'format_specs': {
                        'category': {'case': 'upper'},
                        'score': {'decimal_places': 1}
                    }
                },
                # Finally validate
                {
                    'type': 'validate',
                    'rules': [
                        {'column': 'name', 'type': 'not_null'},
                        {
                            'column': 'score',
                            'type': 'range',
                            'min': 0,
                            'max': 100
                        }
                    ]
                }
            ]
        )
        
        # Verify the entire transformation chain
        assert result.transformed_data is not None
        assert result.quality_metrics is not None
        
        # Check data cleaning
        names = [row.name for row in result.transformed_data.collect()]
        assert 'Alice' in names  # Whitespace removed
        assert 'UNKNOWN' in names  # Null replaced
        
        # Check type conversion
        schema = result.transformed_data.schema
        assert isinstance(schema['score'].dataType, DoubleType)
        assert isinstance(schema['active'].dataType, BooleanType)
        
        # Check formatting
        categories = [
            row.category
            for row in result.transformed_data.collect()
        ]
        assert all(cat in ['A', 'B'] for cat in categories)
        
        # Check validations
        assert len(result.quality_metrics.validation_errors) > 0
        assert any('outside range' in err for err in result.quality_metrics.validation_errors) 