"""
Tests for Stage 3 utility functions
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType
)

from src.stages.stage3_data_quality.utils import (
    calculate_column_statistics,
    detect_data_patterns,
    check_value_distribution,
    validate_value_ranges,
    check_referential_integrity
)


@pytest.fixture(scope="session")
def spark():
    """Create a SparkSession for testing."""
    return SparkSession.builder \
        .appName("Stage3UtilsTests") \
        .master("local[*]") \
        .getOrCreate()


@pytest.fixture
def numeric_df(spark):
    """Create a sample DataFrame with numeric data."""
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("value", FloatType(), True)
    ])

    data = [
        (1, 10.5),
        (2, 20.0),
        (3, -5.5),
        (4, 15.0),
        (5, None)
    ]

    return spark.createDataFrame(data, schema)


@pytest.fixture
def string_df(spark):
    """Create a sample DataFrame with string data."""
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("text", StringType(), True)
    ])

    data = [
        (1, "Hello123"),
        (2, "World!"),
        (3, "Test"),
        (4, None),
        (5, "Special@Chars")
    ]

    return spark.createDataFrame(data, schema)


def test_calculate_column_statistics(numeric_df):
    """Test calculation of column statistics."""
    stats = calculate_column_statistics(numeric_df, "value")

    assert "count" in stats
    assert "distinct_count" in stats
    assert "mean" in stats
    assert "stddev" in stats
    assert "min" in stats
    assert "max" in stats

    assert stats["count"] == 4  # Excluding None
    assert stats["min"] == -5.5
    assert stats["max"] == 20.0


def test_detect_data_patterns_numeric(numeric_df):
    """Test pattern detection for numeric data."""
    patterns = detect_data_patterns(numeric_df, "value")

    assert "is_continuous" in patterns
    assert "has_negatives" in patterns
    assert "has_decimals" in patterns

    assert patterns["has_negatives"]  # Due to -5.5
    assert patterns["has_decimals"]  # FloatType column


def test_detect_data_patterns_string(string_df):
    """Test pattern detection for string data."""
    patterns = detect_data_patterns(string_df, "text")

    assert "avg_length" in patterns
    assert "max_length" in patterns
    assert "contains_numbers" in patterns
    assert "contains_special" in patterns

    assert patterns["contains_numbers"]  # Due to "Hello123"
    assert patterns["contains_special"]  # Due to "Special@Chars"


def test_check_value_distribution(numeric_df):
    """Test value distribution analysis."""
    distribution = check_value_distribution(numeric_df, "value")

    assert "top_values" in distribution
    assert "null_ratio" in distribution
    assert "unique_ratio" in distribution

    assert distribution["null_ratio"] == 0.2  # 1 null out of 5
    assert distribution["unique_ratio"] == 0.8  # 4 unique values out of 5


def test_validate_value_ranges(numeric_df):
    """Test value range validation."""
    validation = validate_value_ranges(
        numeric_df,
        "value",
        min_value=0.0,
        max_value=15.0
    )

    assert not validation["is_valid"]  # Due to -5.5 and 20.0
    assert validation["violations"] == 2  # Two values outside range


def test_check_referential_integrity(spark):
    """Test referential integrity checking."""
    df1 = spark.createDataFrame(
        [(1, "A"), (2, "B"), (3, "C")],
        ["id", "name"]
    )

    df2 = spark.createDataFrame(
        [(1, "X"), (2, "Y"), (4, "Z")],
        ["ref_id", "value"]
    )

    integrity = check_referential_integrity(df1, df2, "id", "ref_id")

    assert not integrity["is_valid"]
    assert integrity["orphaned_records"] == 1  # id=3 has no reference
    assert integrity["missing_references"] == 1  # ref_id=4 has no source


def test_calculate_column_statistics_empty(spark):
    """Test statistics calculation with empty DataFrame."""
    empty_df = spark.createDataFrame([], StructType([
        StructField("value", FloatType(), True)
    ]))

    stats = calculate_column_statistics(empty_df, "value")

    assert stats["count"] == 0
    assert stats["distinct_count"] == 0
    assert stats["mean"] is None
    assert stats["stddev"] is None


def test_check_value_distribution_all_null(spark):
    """Test distribution analysis with all null values."""
    schema = StructType([
        StructField("value", FloatType(), True)
    ])

    null_df = spark.createDataFrame(
        [(None,), (None,), (None,)],
        schema
    )

    distribution = check_value_distribution(null_df, "value")

    assert distribution["null_ratio"] == 1.0
    assert distribution["unique_ratio"] == 0.0
    assert len(distribution["top_values"]) == 0 