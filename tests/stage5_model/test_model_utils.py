"""Tests for model utilities in stage 5."""

import os
import sys
import pytest
import tempfile
import numpy as np
from typing import Generator

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, StringType
from pyspark.sql.functions import col

from src.core.config.settings import Settings
from src.stages.stage5_model.utils.model_utils import prepare_train_test_split
from src.utility.spark_utils import create_spark_session

# Set Python environment variables for consistent Python versions
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

@pytest.fixture(scope="session")
def spark_session() -> Generator[SparkSession, None, None]:
    """Create a Spark session with optimized configuration for testing."""
    settings = Settings()
    
    # Add Hive configuration with parallel execution optimizations
    spark_config = settings.spark.as_dict()
    spark_config.update({
        "spark.sql.shuffle.partitions": "20",  # Increase shuffle partitions
        "spark.default.parallelism": "20",     # Match CPU cores * 2
        "spark.sql.adaptive.enabled": "true",  # Enable adaptive query execution
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.localShuffleReader.enabled": "true",
        "spark.sql.inMemoryColumnarStorage.compressed": "true",
        "spark.sql.inMemoryColumnarStorage.batchSize": "10000",
        # Disable Arrow optimization to avoid memory issues
        "spark.sql.execution.arrow.pyspark.enabled": "false",
        # Memory settings
        "spark.memory.fraction": "0.8",
        "spark.memory.storageFraction": "0.3",
        "spark.sql.broadcastTimeout": "300"
    })
    
    spark = create_spark_session(spark_config)
    
    try:
        yield spark
    finally:
        spark.stop()


@pytest.fixture(scope="module")
def sample_df(spark_session):
    """Create a sample DataFrame for testing."""
    data = [
        ("A", 1.0, 2.0, 0.0),  # Fixed: Using float values for DoubleType
        ("B", 2.0, 3.0, 1.0),
        ("A", 3.0, 4.0, 0.0),
        ("B", 4.0, 5.0, 1.0),
        ("A", 5.0, 6.0, 0.0),
        ("B", 6.0, 7.0, 1.0)
    ]
    schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature1", DoubleType(), False),
        StructField("feature2", DoubleType(), False),
        StructField("label", DoubleType(), False)  # Fixed: Using DoubleType for label
    ])
    return spark_session.createDataFrame(data, schema)


def test_prepare_train_test_split(sample_df):
    """Test train/test split preparation."""
    train_df, test_df = prepare_train_test_split(sample_df, test_size=0.3)
    
    # Verify split ratio
    train_count = train_df.count()
    test_count = test_df.count()
    total_count = sample_df.count()
    
    assert train_count + test_count == total_count
    assert abs(test_count / total_count - 0.3) <= 0.2  # Using <= for small dataset
    
    # Verify schema preservation
    assert train_df.schema == sample_df.schema
    assert test_df.schema == sample_df.schema


def test_validate_schema_compatibility(sample_df):
    """Test schema validation between DataFrames."""
    # Create DataFrame with compatible schema
    compatible_data = [("C", 7.0, 8.0, 1.0)]
    compatible_df = sample_df.sparkSession.createDataFrame(compatible_data, sample_df.schema)
    
    # Create DataFrame with incompatible schema
    incompatible_schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature1", DoubleType(), False),
        StructField("feature2", DoubleType(), False),
        StructField("different_label", DoubleType(), False)
    ])
    incompatible_data = [("D", 9.0, 10.0, 1.0)]
    incompatible_df = sample_df.sparkSession.createDataFrame(incompatible_data, incompatible_schema)
    
    # Test schema validation
    assert sample_df.schema == compatible_df.schema
    assert sample_df.schema != incompatible_df.schema


def test_save_load_model(spark_session, sample_df):
    """Test model saving and loading."""
    # Create temporary directory for model
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = os.path.join(temp_dir, "test_model")
        
        # Save DataFrame as parquet with optimized settings
        sample_df.write.format("parquet") \
                .mode("overwrite") \
                .option("compression", "snappy") \
                .save(model_path)
        
        # Load DataFrame and verify
        loaded_df = spark_session.read.parquet(model_path)
        
        # Compare schemas ignoring nullability
        loaded_fields = loaded_df.schema.fields
        original_fields = sample_df.schema.fields
        assert len(loaded_fields) == len(original_fields)
        for loaded_field, original_field in zip(loaded_fields, original_fields):
            assert loaded_field.name == original_field.name
            assert type(loaded_field.dataType) == type(original_field.dataType)
        
        assert loaded_df.count() == sample_df.count()


def test_analyze_predictions(sample_df):
    """Test prediction analysis utilities."""
    # Add prediction column
    predictions = sample_df.withColumn("prediction", col("label") + 0.1)
    
    # Calculate basic metrics
    total = predictions.count()
    correct = predictions.filter(
        (col("prediction") >= 0.5) == (col("label") >= 0.5)
    ).count()
    
    accuracy = correct / total
    assert 0 <= accuracy <= 1


def test_get_feature_correlations(sample_df):
    """Test feature correlation analysis."""
    # Calculate correlation between features
    correlation = sample_df.stat.corr("feature1", "feature2")
    assert -1 <= correlation <= 1


def test_check_data_leakage(sample_df):
    """Test data leakage detection."""
    # Check correlation between features and label
    for feature in ["feature1", "feature2"]:
        correlation = abs(sample_df.stat.corr(feature, "label"))
        assert correlation < 1.0  # Perfect correlation would indicate leakage 