"""
Tests for Stage 4 Analytics functionality
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
    StringType,
    TimestampType
)
from datetime import datetime, timedelta
from src.stages.stage4_analytics.analytics import DataAnalyzer
from src.stages.stage4_analytics.config import AnalyticsConfig

@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing."""
    return SparkSession.builder \
        .appName("Stage4AnalyticsTests") \
        .master("local[*]") \
        .getOrCreate()

@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    return StructType([
        StructField("id", StringType(), True),
        StructField("value1", FloatType(), True),
        StructField("value2", FloatType(), True),
        StructField("group", StringType(), True),
        StructField("timestamp", TimestampType(), True)
    ])

@pytest.fixture
def sample_data(spark, sample_schema):
    """Create sample data for testing."""
    base_time = datetime.now()
    data = [
        ("1", 10.0, 5.0, "A", base_time),
        ("2", 15.0, 7.5, "A", base_time + timedelta(days=1)),
        ("3", 20.0, 10.0, "B", base_time + timedelta(days=2)),
        ("4", 25.0, 12.5, "B", base_time + timedelta(days=3)),
        ("5", 30.0, 15.0, "C", base_time + timedelta(days=4))
    ]
    
    return spark.createDataFrame(data, sample_schema)

@pytest.fixture
def analyzer(spark):
    """Create a DataAnalyzer instance."""
    return DataAnalyzer(spark)

@pytest.fixture
def config():
    """Create an AnalyticsConfig instance."""
    return AnalyticsConfig()

def test_summary_statistics(analyzer, sample_data):
    """Test calculation of summary statistics."""
    stats = analyzer.calculate_summary_statistics(
        sample_data,
        ["value1", "value2"]
    )
    
    assert "value1" in stats
    assert "value2" in stats
    assert abs(stats["value1"]["mean"] - 20.0) < 0.01
    assert abs(stats["value2"]["mean"] - 10.0) < 0.01

def test_correlations(analyzer, sample_data):
    """Test correlation calculation."""
    correlations = analyzer.calculate_correlations(
        sample_data,
        ["value1", "value2"],
        method="pearson"
    )
    
    assert len(correlations) > 0
    assert abs(correlations[("value1", "value2")] - 1.0) < 0.01

def test_group_statistics(analyzer, sample_data):
    """Test group statistics calculation."""
    group_stats = analyzer.calculate_group_statistics(
        sample_data,
        group_columns=["group"],
        agg_columns=["value1"],
        agg_functions=["avg", "stddev"]
    )
    
    assert group_stats.count() == 3
    row = group_stats.filter(group_stats.group == "A").collect()[0]
    assert abs(row["value1_avg"] - 12.5) < 0.01

def test_time_series_metrics(analyzer, sample_data):
    """Test time series metrics calculation."""
    ts_metrics = analyzer.calculate_time_series_metrics(
        sample_data,
        time_column="timestamp",
        metric_columns=["value1"],
        window_size=3
    )
    
    assert ts_metrics.count() == 5
    assert "value1_rolling_avg" in ts_metrics.columns

def test_outlier_detection(analyzer, sample_data):
    """Test outlier detection."""
    result = analyzer.detect_outliers(
        sample_data,
        columns=["value1"],
        method="iqr",
        threshold=1.5
    )
    
    assert "value1_is_outlier" in result.columns
    assert result.filter(result.value1_is_outlier).count() >= 0

def test_analytics_report(analyzer, sample_data, config):
    """Test analytics report generation."""
    custom_config = config.create_config(
        numeric_columns=["value1", "value2"],
        correlation_columns=["value1", "value2"],
        correlation_method="pearson",
        group_columns=["group"],
        agg_columns=["value1"],
        agg_functions=["avg", "stddev"],
        time_column="timestamp",
        metric_columns=["value1"],
        window_size=3,
        outlier_columns=["value1"],
        outlier_method="iqr",
        outlier_threshold=1.5
    )
    
    report = analyzer.generate_analytics_report(sample_data, custom_config)
    
    assert "summary_statistics" in report
    assert "correlations" in report
    assert "group_statistics" in report
    assert "time_series_metrics" in report
    assert "outliers" in report

def test_config_validation(config):
    """Test configuration validation."""
    valid_config = config.create_config(
        numeric_columns=["value1"],
        correlation_method="pearson"
    )
    
    assert config.validate_config(valid_config)
    
    invalid_config = valid_config.copy()
    invalid_config["correlation_method"] = "invalid"
    
    assert not config.validate_config(invalid_config)

def test_invalid_column_handling(analyzer, sample_data):
    """Test handling of invalid column names."""
    with pytest.raises(Exception):
        analyzer.calculate_summary_statistics(sample_data, ["invalid_column"])

def test_empty_dataframe_handling(analyzer, spark, sample_schema):
    """Test handling of empty DataFrames."""
    empty_df = spark.createDataFrame([], sample_schema)
    
    stats = analyzer.calculate_summary_statistics(empty_df, ["value1"])
    assert all(v is None for v in stats["value1"].values()) 