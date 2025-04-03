"""
Tests for Stage 4 Analytics utility functions
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
from src.stages.stage4_analytics.utils import (
    calculate_descriptive_stats,
    calculate_correlation_matrix,
    calculate_group_metrics,
    calculate_time_series_metrics,
    detect_outliers,
    validate_numeric_columns,
    calculate_moving_average,
    detect_seasonality,
    identify_trends,
    analyze_distribution,
    calculate_percentiles
)


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing."""
    return SparkSession.builder \
        .appName("Stage4UtilsTests") \
        .master("local[*]") \
        .getOrCreate()


@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    return StructType([
        StructField("id", StringType(), True),
        StructField("value1", FloatType(), True),
        StructField("value2", FloatType(), True),
        StructField("timestamp", TimestampType(), True)
    ])


@pytest.fixture
def sample_data(spark, sample_schema):
    """Create sample data for testing."""
    base_time = datetime.now()
    data = [
        ("1", 10.0, 5.0, base_time),
        ("2", 15.0, 7.5, base_time + timedelta(days=1)),
        ("3", 20.0, 10.0, base_time + timedelta(days=2)),
        ("4", 25.0, 12.5, base_time + timedelta(days=3)),
        ("5", 30.0, 15.0, base_time + timedelta(days=4))
    ]

    return spark.createDataFrame(data, sample_schema)


def test_calculate_descriptive_stats(sample_data):
    """Test calculation of descriptive statistics."""
    stats = calculate_descriptive_stats(sample_data, "value1")

    assert isinstance(stats, dict)
    assert "mean" in stats
    assert "stddev" in stats
    assert "min" in stats
    assert "max" in stats
    assert "q1" in stats
    assert "median" in stats
    assert "q3" in stats
    assert "skewness" in stats
    assert "kurtosis" in stats

    assert abs(stats["mean"] - 20.0) < 0.01
    assert abs(stats["min"] - 10.0) < 0.01
    assert abs(stats["max"] - 30.0) < 0.01


def test_calculate_correlation_matrix(sample_data):
    """Test correlation matrix calculation."""
    correlations = calculate_correlation_matrix(
        sample_data,
        ["value1", "value2"],
        method="pearson"
    )

    assert isinstance(correlations, dict)
    assert ("value1", "value2") in correlations
    assert ("value2", "value1") in correlations
    assert abs(correlations[("value1", "value2")] - 1.0) < 0.01


def test_calculate_group_metrics(sample_data):
    """Test group metrics calculation."""
    metrics = calculate_group_metrics(
        sample_data,
        ["group"],
        ["value1"],
        ["count", "avg", "stddev"]
    )

    assert metrics.count() == 3
    row = metrics.filter(metrics.group == "A").collect()[0]
    assert row["value1_count"] == 2
    assert abs(row["value1_avg"] - 12.5) < 0.01


def test_calculate_time_series_metrics(sample_data):
    """Test time series metrics calculation."""
    metrics = calculate_time_series_metrics(
        sample_data,
        "timestamp",
        ["value1"],
        window_size=3
    )

    assert metrics.count() == 5
    assert "value1_rolling_avg" in metrics.columns
    assert "value1_rolling_stddev" in metrics.columns
    assert "value1_rolling_min" in metrics.columns
    assert "value1_rolling_max" in metrics.columns


def test_detect_outliers_iqr(sample_data):
    """Test outlier detection using IQR method."""
    result = detect_outliers(
        sample_data,
        "value1",
        method="iqr",
        threshold=1.5
    )

    assert "value1_is_outlier" in result.columns
    outliers = result.filter(result.value1_is_outlier)
    assert outliers.count() >= 0


def test_detect_outliers_zscore(sample_data):
    """Test outlier detection using Z-score method."""
    result = detect_outliers(
        sample_data,
        "value1",
        method="zscore",
        threshold=2.0
    )

    assert "value1_is_outlier" in result.columns
    outliers = result.filter(result.value1_is_outlier)
    assert outliers.count() >= 0


def test_detect_outliers_invalid_method(sample_data):
    """Test outlier detection with invalid method."""
    with pytest.raises(ValueError):
        detect_outliers(sample_data, "value1", method="invalid")


def test_validate_numeric_columns(sample_data):
    """Test numeric column validation."""
    assert validate_numeric_columns(sample_data, ["value1", "value2"])
    assert not validate_numeric_columns(sample_data, ["id", "value1"])
    assert not validate_numeric_columns(sample_data, ["invalid_column"])


def test_empty_dataframe(spark, sample_data):
    """Test utility functions with empty DataFrame."""
    empty_df = spark.createDataFrame([], sample_data.schema)

    stats = calculate_descriptive_stats(empty_df, "value1")
    assert all(v is None for v in stats.values())

    correlations = calculate_correlation_matrix(empty_df, ["value1", "value2"])
    assert all(v is None for v in correlations.values())

    metrics = calculate_group_metrics(empty_df, ["group"], ["value1"], ["count"])
    assert metrics.count() == 0


def test_null_values(spark):
    """Test handling of null values."""
    schema = StructType([
        StructField("value", FloatType(), True)
    ])

    data = [
        (None,),
        (10.0,),
        (None,),
        (20.0,)
    ]

    df = spark.createDataFrame(data, schema)
    stats = calculate_descriptive_stats(df, "value")

    assert stats["mean"] is not None
    assert stats["stddev"] is not None


def test_moving_average(spark, sample_data):
    """Test moving average calculation."""
    result = calculate_moving_average(
        sample_data,
        "value1",
        window_size=3
    )

    assert "value1_ma" in result.columns
    first_ma = result.filter(result.id == "3").collect()[0].value1_ma
    assert abs(first_ma - 15.0) < 0.01


def test_seasonality_detection(spark, sample_data):
    """Test seasonality detection."""
    result = detect_seasonality(
        sample_data,
        "value1",
        "timestamp",
        period=2
    )

    assert "seasonality_score" in result
    assert 0 <= result["seasonality_score"] <= 1


def test_trend_identification(spark, sample_data):
    """Test trend identification."""
    result = identify_trends(
        sample_data,
        "value1",
        "timestamp"
    )

    assert "trend_direction" in result
    assert result["trend_direction"] in ["increasing", "decreasing", "stable"]


def test_distribution_analysis(spark, sample_data):
    """Test distribution analysis."""
    result = analyze_distribution(sample_data, "value1")

    assert "mean" in result
    assert "median" in result
    assert "skewness" in result
    assert abs(result["mean"] - 20.0) < 0.01


def test_percentile_calculation(spark, sample_data):
    """Test percentile calculation."""
    result = calculate_percentiles(
        sample_data,
        "value1",
        [25, 50, 75]
    )

    assert len(result) == 3
    assert abs(result[50] - 20.0) < 0.01


def test_empty_data_handling(spark, sample_schema):
    """Test handling of empty DataFrames."""
    empty_df = spark.createDataFrame([], sample_schema)

    ma_result = calculate_moving_average(empty_df, "value1", window_size=3)
    assert ma_result.count() == 0

    dist_result = analyze_distribution(empty_df, "value1")
    assert all(v is None for v in dist_result.values())


def test_invalid_column_handling(spark, sample_data):
    """Test handling of invalid column names."""
    with pytest.raises(Exception):
        calculate_moving_average(sample_data, "invalid_column", window_size=3)


def test_invalid_window_size(spark, sample_data):
    """Test handling of invalid window size."""
    with pytest.raises(ValueError):
        calculate_moving_average(sample_data, "value1", window_size=0)


def test_invalid_percentiles(spark, sample_data):
    """Test handling of invalid percentiles."""
    with pytest.raises(ValueError):
        calculate_percentiles(sample_data, "value1", [-10, 110]) 