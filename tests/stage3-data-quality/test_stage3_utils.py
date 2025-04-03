"""
Tests for stage 3 data quality utility functions
"""

import pytest
from pyspark.sql.types import (
    StructType, StructField, IntegerType, FloatType, StringType
)
from src.stages.stage3_data_quality.utils import (
    calculate_column_statistics,
    detect_data_patterns,
    check_value_distribution,
    validate_value_ranges,
    check_referential_integrity
)
from tests.base_test_config import BaseSparkTest

class TestStage3Utils(BaseSparkTest):
    """Test cases for stage 3 data quality utility functions"""

    @classmethod
    def setup_class(cls):
        """Set up test environment for the class"""
        super().setup_class()
        cls.spark = cls._spark

    def test_calculate_column_statistics(self):
        """Test calculation of column statistics."""
        # Create test data
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
        df = self.spark.createDataFrame(data, schema)
        
        # Calculate statistics
        stats = calculate_column_statistics(df, "value")
        
        # Verify results
        assert stats["count"] == 5
        assert stats["null_count"] == 1
        assert abs(stats["mean"] - 10.0) < 0.01
        assert abs(stats["stddev"] - 11.04) < 0.01
        assert stats["min"] == -5.5
        assert stats["max"] == 20.0

    def test_detect_data_patterns_numeric(self):
        """Test pattern detection for numeric data."""
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
        df = self.spark.createDataFrame(data, schema)
        
        patterns = detect_data_patterns(df, "value")
        
        assert patterns["null_percentage"] == 20.0
        assert patterns["unique_values"] == 4
        assert patterns["negative_values"] == 1

    def test_detect_data_patterns_string(self):
        """Test pattern detection for string data."""
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
        df = self.spark.createDataFrame(data, schema)
        
        patterns = detect_data_patterns(df, "text")
        
        assert patterns["null_percentage"] == 20.0
        assert patterns["unique_values"] == 4
        assert patterns["avg_length"] > 0

    def test_check_value_distribution(self):
        """Test value distribution analysis."""
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
        df = self.spark.createDataFrame(data, schema)
        
        distribution = check_value_distribution(df, "value")
        
        assert "percentiles" in distribution
        assert len(distribution["percentiles"]) > 0
        assert "histogram" in distribution
        assert len(distribution["histogram"]) > 0

    def test_validate_value_ranges(self):
        """Test value range validation."""
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
        df = self.spark.createDataFrame(data, schema)
        
        validation = validate_value_ranges(df, "value", min_value=0, max_value=15)
        
        assert validation["below_min"] == 1
        assert validation["above_max"] == 1
        assert validation["within_range"] == 2
        assert validation["null_values"] == 1

    def test_check_referential_integrity(self):
        """Test referential integrity checking."""
        df1 = self.spark.createDataFrame(
            [(1, "A"), (2, "B"), (3, "C")],
            ["id", "name"]
        )
        df2 = self.spark.createDataFrame(
            [(1, 100), (2, 200), (4, 400)],
            ["id", "value"]
        )
        
        integrity = check_referential_integrity(df1, df2, "id")
        
        assert integrity["matching_keys"] == 2
        assert integrity["missing_in_first"] == 1
        assert integrity["missing_in_second"] == 1

    def test_calculate_column_statistics_empty(self):
        """Test statistics calculation with empty DataFrame."""
        empty_df = self.spark.createDataFrame([], StructType([
            StructField("value", FloatType(), True)
        ]))
        
        stats = calculate_column_statistics(empty_df, "value")
        
        assert stats["count"] == 0
        assert stats["null_count"] == 0
        assert stats["mean"] is None
        assert stats["stddev"] is None
        assert stats["min"] is None
        assert stats["max"] is None

    def test_check_value_distribution_all_null(self):
        """Test distribution analysis with all null values."""
        schema = StructType([
            StructField("value", FloatType(), True)
        ])
        
        null_df = self.spark.createDataFrame(
            [(None,), (None,), (None,)],
            schema
        )
        
        distribution = check_value_distribution(null_df, "value")
        
        assert distribution["percentiles"] == []
        assert distribution["histogram"] == [] 