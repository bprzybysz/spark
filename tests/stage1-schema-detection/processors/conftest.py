"""
Test fixtures for stage1 schema detection processor tests.
"""

import os
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark_session():
    """Create a SparkSession for testing.
    
    Returns:
        SparkSession: The active SparkSession
    """
    spark = (SparkSession.builder
             .appName("schema-detection-test")
             .master("local[1]")
             .config("spark.sql.warehouse.dir", os.path.join(os.getcwd(), "spark-warehouse"))
             .config("spark.driver.memory", "512m")
             .config("spark.executor.memory", "512m")
             .config("spark.ui.enabled", "false")
             .config("spark.sql.session.timeZone", "UTC")
             .getOrCreate())
    
    yield spark
    
    spark.stop() 