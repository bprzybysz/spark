"""
Common test fixtures for stage 3 data quality tests
"""

import os
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    TimestampType
)
from datetime import datetime
from tests.base_test_config import BaseSparkTest

class Stage3Test(BaseSparkTest):
    """Base class for stage 3 tests with specific configurations"""
    pass

@pytest.fixture(scope="session")
def spark():
    """Create a reusable Spark session for all tests."""
    test = Stage3Test()
    test.setup_class()
    yield test.spark
    test.teardown_class()

@pytest.fixture(scope="session")
def test_data_path():
    """Get the path to test data directory."""
    return os.path.join(os.getcwd(), "tests", "stage3-data-quality", "data")

@pytest.fixture(scope="session", autouse=True)
def cleanup_spark(spark):
    """Cleanup Spark session after all tests."""
    yield
    spark.stop()

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
        ("2", 15.0, 7.5, base_time),
        ("3", 20.0, 10.0, base_time),
        ("4", 25.0, 12.5, base_time),
        ("5", 30.0, 15.0, base_time)
    ]
    return spark.createDataFrame(data, sample_schema)

@pytest.fixture
def edge_case_schema():
    """Create schema for edge case testing."""
    return StructType([
        StructField("id", StringType(), True),
        StructField("nullable_value", FloatType(), True),
        StructField("special_chars", StringType(), True),
        StructField("timestamp", TimestampType(), True)
    ])

@pytest.fixture
def edge_case_data(spark, edge_case_schema):
    """Create edge case data for testing."""
    base_time = datetime.now()
    data = [
        ("1", None, "@#$%", base_time),
        ("2", -999.99, "Normal", base_time),
        ("3", 0.0, "", base_time),
        ("4", float('inf'), "Mixed123", base_time),
        ("5", None, None, base_time)
    ]
    return spark.createDataFrame(data, edge_case_schema)

@pytest.fixture
def reference_schema():
    """Create schema for referential integrity testing."""
    return StructType([
        StructField("ref_id", StringType(), True),
        StructField("ref_value", StringType(), True)
    ])

@pytest.fixture
def reference_data(spark, reference_schema):
    """Create reference data for testing."""
    data = [
        ("1", "RefA"),
        ("2", "RefB"),
        ("3", "RefC"),
        ("6", "RefD")  # Intentional mismatch with sample data
    ]
    return spark.createDataFrame(data, reference_schema) 