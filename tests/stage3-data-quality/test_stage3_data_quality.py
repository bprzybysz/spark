"""
Tests for Stage 3 Data Quality functionality
"""

import pytest
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
    StringType
)
from tests.base_test_config import BaseSparkTest
from src.stages.stage3_data_quality.data_quality import DataQualityChecker
from src.stages.stage3_data_quality.config import DataQualityConfig


class TestStage3DataQuality(BaseSparkTest):
    """Test suite for Stage 3 Data Quality functionality"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.checker = DataQualityChecker(self.spark)
        self.config = DataQualityConfig()
        
        # Create sample schema
        self.sample_schema = StructType([
            StructField("id", StringType(), True),
            StructField("value1", FloatType(), True),
            StructField("value2", FloatType(), True)
        ])
        
        # Create sample data
        self.sample_data = [
            ("1", 10.0, 5.0),
            ("2", 15.0, 7.5),
            ("3", 20.0, 10.0),
            ("4", 25.0, 12.5),
            ("5", 30.0, 15.0)
        ]
        self.df = self.spark.createDataFrame(self.sample_data, self.sample_schema)

    def test_completeness_validation(self):
        """Test completeness validation."""
        result = self.checker.validate_completeness(self.df, ["value1", "value2"])
        assert result["value1"]["completeness"] == 1.0
        assert result["value2"]["completeness"] == 1.0

    def test_data_type_validation(self):
        """Test data type validation."""
        result = self.checker.validate_data_types(
            self.df,
            {"value1": "float", "value2": "float"}
        )
        assert result["value1"]["is_valid"]
        assert result["value2"]["is_valid"]

    def test_anomaly_detection(self):
        """Test anomaly detection."""
        result = self.checker.detect_anomalies(
            self.df,
            ["value1"],
            method="zscore",
            threshold=2.0
        )
        assert "value1_anomaly" in result.columns

    def test_quality_metrics(self):
        """Test quality metrics calculation."""
        metrics = self.checker.calculate_quality_metrics(
            self.df,
            ["value1", "value2"]
        )
        assert metrics["value1"]["mean"] is not None
        assert metrics["value2"]["stddev"] is not None

    def test_quality_report(self):
        """Test quality report generation."""
        custom_config = self.config.create_config(
            completeness_threshold=0.8,
            data_types={"value1": "float", "value2": "float"},
            anomaly_columns=["value1"],
            anomaly_method="zscore",
            anomaly_threshold=2.0
        )

        report = self.checker.generate_quality_report(self.df, custom_config)
        assert "completeness" in report
        assert "data_types" in report
        assert "anomalies" in report
        assert "metrics" in report

    def test_config_validation(self):
        """Test configuration validation."""
        valid_config = self.config.create_config(
            completeness_threshold=0.8,
            data_types={"value1": "float"}
        )
        assert self.config.validate_config(valid_config)

        invalid_config = valid_config.copy()
        invalid_config["completeness_threshold"] = -1.0
        assert not self.config.validate_config(invalid_config)

    def test_invalid_column_handling(self):
        """Test handling of invalid column names."""
        with pytest.raises(Exception):
            self.checker.validate_completeness(self.df, ["invalid_column"])

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        empty_df = self.spark.createDataFrame([], self.sample_schema)
        result = self.checker.validate_completeness(empty_df, ["value1"])
        assert result["value1"]["completeness"] == 1.0 