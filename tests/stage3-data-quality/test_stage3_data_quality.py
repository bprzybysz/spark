"""
Tests for Stage 3 Data Quality functionality
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
    StringType
)
from src.stages.stage3_data_quality.data_quality import DataQualityChecker
from src.stages.stage3_data_quality.config import DataQualityConfig


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing."""
    return SparkSession.builder \
        .appName("Stage3DataQualityTests") \
        .master("local[*]") \
        .getOrCreate()


@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    return StructType([
        StructField("id", StringType(), True),
        StructField("value1", FloatType(), True),
        StructField("value2", FloatType(), True)
    ])


@pytest.fixture
def sample_data(spark, sample_schema):
    """Create sample data for testing."""
    data = [
        ("1", 10.0, 5.0),
        ("2", 15.0, 7.5),
        ("3", 20.0, 10.0),
        ("4", 25.0, 12.5),
        ("5", 30.0, 15.0)
    ]
    return spark.createDataFrame(data, sample_schema)


@pytest.fixture
def checker(spark):
    """Create a DataQualityChecker instance."""
    return DataQualityChecker(spark)


@pytest.fixture
def config():
    """Create a DataQualityConfig instance."""
    return DataQualityConfig()


def test_completeness_validation(checker, sample_data):
    """Test completeness validation."""
    result = checker.validate_completeness(sample_data, ["value1", "value2"])
    assert result["value1"]["completeness"] == 1.0
    assert result["value2"]["completeness"] == 1.0


def test_data_type_validation(checker, sample_data):
    """Test data type validation."""
    result = checker.validate_data_types(
        sample_data,
        {"value1": "float", "value2": "float"}
    )
    assert result["value1"]["is_valid"]
    assert result["value2"]["is_valid"]


def test_anomaly_detection(checker, sample_data):
    """Test anomaly detection."""
    result = checker.detect_anomalies(
        sample_data,
        ["value1"],
        method="zscore",
        threshold=2.0
    )
    assert "value1_anomaly" in result.columns


def test_quality_metrics(checker, sample_data):
    """Test quality metrics calculation."""
    metrics = checker.calculate_quality_metrics(
        sample_data,
        ["value1", "value2"]
    )
    assert metrics["value1"]["mean"] is not None
    assert metrics["value2"]["stddev"] is not None


def test_quality_report(checker, sample_data, config):
    """Test quality report generation."""
    custom_config = config.create_config(
        completeness_threshold=0.8,
        data_types={"value1": "float", "value2": "float"},
        anomaly_columns=["value1"],
        anomaly_method="zscore",
        anomaly_threshold=2.0
    )

    report = checker.generate_quality_report(sample_data, custom_config)
    assert "completeness" in report
    assert "data_types" in report
    assert "anomalies" in report
    assert "metrics" in report


def test_config_validation(config):
    """Test configuration validation."""
    valid_config = config.create_config(
        completeness_threshold=0.8,
        data_types={"value1": "float"}
    )
    assert config.validate_config(valid_config)

    invalid_config = valid_config.copy()
    invalid_config["completeness_threshold"] = -1.0
    assert not config.validate_config(invalid_config)


def test_invalid_column_handling(checker, sample_data):
    """Test handling of invalid column names."""
    with pytest.raises(Exception):
        checker.validate_completeness(sample_data, ["invalid_column"])


def test_empty_dataframe_handling(checker, spark, sample_schema):
    """Test handling of empty DataFrames."""
    empty_df = spark.createDataFrame([], sample_schema)
    result = checker.validate_completeness(empty_df, ["value1"])
    assert result["value1"]["completeness"] == 1.0 