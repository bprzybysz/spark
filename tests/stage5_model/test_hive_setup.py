"""Tests for Hive setup and data preparation in stage 5."""

import os
import sys
import pytest
import shutil
import tempfile
import threading
import concurrent.futures
from typing import Generator, List, Dict, Any

import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, IntegerType, BooleanType
from pyspark.sql.functions import col, expr, when, isnull

from src.core.config.settings import Settings
from src.stages.stage5_model.utils.model_utils import prepare_train_test_split
from src.utility.spark_utils import create_spark_session

# Set Python environment variables for consistent Python versions
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


@pytest.fixture(scope="session")
def hive_warehouse_dir() -> Generator[str, None, None]:
    """Create a temporary Hive warehouse directory."""
    temp_dir = tempfile.mkdtemp(prefix="hive_warehouse_")
    os.environ["SPARK_WAREHOUSE_DIR"] = temp_dir
    
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def spark_session(hive_warehouse_dir: str) -> Generator[SparkSession, None, None]:
    """Create a Spark session with Hive support for testing."""
    settings = Settings()
    
    # Configure Hadoop home and native libraries
    hadoop_home = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hadoop")
    os.environ["HADOOP_HOME"] = hadoop_home
    os.makedirs(os.path.join(hadoop_home, "bin"), exist_ok=True)
    
    # Create empty winutils file for compatibility
    with open(os.path.join(hadoop_home, "bin", "winutils"), "w") as f:
        pass
    os.chmod(os.path.join(hadoop_home, "bin", "winutils"), 0o755)
    
    # Add Hive configuration
    spark_config = settings.spark.as_dict()
    spark_config.update({
        "spark.sql.warehouse.dir": hive_warehouse_dir,
        "spark.sql.catalogImplementation": "hive",
        "spark.hadoop.javax.jdo.option.ConnectionURL": f"jdbc:derby:;databaseName={hive_warehouse_dir}/metastore_db;create=true",
        "spark.hadoop.datanucleus.schema.autoCreateAll": "true",
        "spark.hadoop.hive.metastore.schema.verification": "false"
    })
    
    spark = create_spark_session(spark_config)
    
    try:
        yield spark
    finally:
        spark.stop()
        shutil.rmtree(hadoop_home, ignore_errors=True)


def generate_test_data(num_rows: int = 10000, num_features: int = 50) -> pd.DataFrame:
    """Generate synthetic test data."""
    np.random.seed(42)
    X = np.random.randn(num_rows, num_features)
    y = np.sum(X * np.random.randn(num_features), axis=1) + np.random.randn(num_rows)
    
    # Create DataFrame with features and target
    feature_cols = [f"feature_{i}" for i in range(num_features)]
    df = pd.DataFrame(X, columns=feature_cols)
    df["target"] = y
    df["partition_id"] = np.arange(num_rows) % 10  # Add partition column
    
    return df


def prepare_hive_tables(spark: SparkSession, test_data: pd.DataFrame) -> None:
    """Prepare Hive tables with test data."""
    # Convert pandas DataFrame to Spark DataFrame
    spark_df = spark.createDataFrame(test_data)
    
    # Save to Hive with partitioning
    spark_df.write.format("parquet") \
            .mode("overwrite") \
            .partitionBy("partition_id") \
            .option("compression", "snappy") \
            .saveAsTable("stage5_test_features")
    
    # Create train/test split tables
    train_df, test_df = prepare_train_test_split(spark_df, test_size=0.2)
    
    train_df.write.format("parquet") \
            .mode("overwrite") \
            .partitionBy("partition_id") \
            .option("compression", "snappy") \
            .saveAsTable("stage5_test_train")
    
    test_df.write.format("parquet") \
           .mode("overwrite") \
           .partitionBy("partition_id") \
           .option("compression", "snappy") \
           .saveAsTable("stage5_test_test")


def parallel_data_read(spark: SparkSession, partition_id: int) -> int:
    """Read data from a specific partition in parallel."""
    df = spark.sql(f"""
        SELECT * FROM stage5_test_features 
        WHERE partition_id = {partition_id}
    """)
    return df.count()


def test_hive_setup(spark_session: SparkSession, hive_warehouse_dir: str):
    """Test Hive setup and warehouse directory."""
    # Check if warehouse directory exists
    assert os.path.exists(hive_warehouse_dir), "Hive warehouse directory not created"
    
    # Check if Hive is enabled
    assert spark_session.conf.get("spark.sql.catalogImplementation") == "hive", \
        "Hive catalog not enabled"
    
    # Verify we can create and query Hive tables
    test_df = spark_session.createDataFrame([(1, "test")], ["id", "value"])
    test_df.write.mode("overwrite").saveAsTable("test_table")
    
    result = spark_session.sql("SHOW TABLES").collect()
    assert any(row.tableName == "test_table" for row in result), \
        "Failed to create Hive table"
    
    # Clean up
    spark_session.sql("DROP TABLE IF EXISTS test_table")


def test_data_preparation(spark_session: SparkSession):
    """Test data preparation and Hive table creation."""
    # Generate and prepare test data
    test_data = generate_test_data()
    prepare_hive_tables(spark_session, test_data)
    
    # Verify tables exist
    tables = spark_session.sql("SHOW TABLES").collect()
    table_names = [row.tableName for row in tables]
    
    assert "stage5_test_features" in table_names, "Features table not created"
    assert "stage5_test_train" in table_names, "Train table not created"
    assert "stage5_test_test" in table_names, "Test table not created"
    
    # Check data integrity
    df = spark_session.table("stage5_test_features")
    row_count = df.count()
    assert row_count == len(test_data), \
        f"Data count mismatch. Expected {len(test_data)}, got {row_count}"
    
    # Verify train/test split
    train_count = spark_session.table("stage5_test_train").count()
    test_count = spark_session.table("stage5_test_test").count()
    assert abs(test_count / row_count - 0.2) < 0.01, "Test split ratio incorrect"
    assert train_count + test_count == row_count, "Train/test split count mismatch"


def test_parallel_data_access(spark_session: SparkSession):
    """Test parallel data access from Hive tables."""
    # Generate and prepare larger test data
    test_data = generate_test_data(num_rows=100000)
    prepare_hive_tables(spark_session, test_data)
    
    # Test parallel reads using ThreadPoolExecutor
    partition_ids = list(range(10))
    expected_counts = [len(test_data) // 10] * 10
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(parallel_data_read, spark_session, pid)
            for pid in partition_ids
        ]
        results = [future.result() for future in futures]
    
    # Verify results
    assert results == expected_counts, \
        "Parallel partition reads returned incorrect counts"
    
    # Test concurrent aggregations
    def parallel_aggregation(partition_id: int) -> Dict[str, float]:
        df = spark_session.sql(f"""
            SELECT 
                partition_id,
                AVG(target) as avg_target,
                STDDEV(target) as std_target
            FROM stage5_test_features 
            WHERE partition_id = {partition_id}
            GROUP BY partition_id
        """)
        result = df.collect()[0]
        return {
            "partition_id": partition_id,
            "avg_target": result.avg_target,
            "std_target": result.std_target
        }
    
    # Run parallel aggregations
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(parallel_aggregation, pid)
            for pid in partition_ids
        ]
        agg_results = [future.result() for future in futures]
    
    # Verify aggregation results
    assert len(agg_results) == 10, "Missing aggregation results"
    for result in agg_results:
        assert "avg_target" in result, "Missing average calculation"
        assert "std_target" in result, "Missing standard deviation calculation"
    
    # Test parallel train/test access
    def parallel_split_access(table_name: str, partition_id: int) -> int:
        df = spark_session.sql(f"""
            SELECT COUNT(*) as cnt FROM {table_name}
            WHERE partition_id = {partition_id}
        """)
        return df.collect()[0].cnt
    
    # Run parallel access to train and test data
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        train_futures = [
            executor.submit(parallel_split_access, "stage5_test_train", pid)
            for pid in partition_ids
        ]
        test_futures = [
            executor.submit(parallel_split_access, "stage5_test_test", pid)
            for pid in partition_ids
        ]
        train_counts = [f.result() for f in train_futures]
        test_counts = [f.result() for f in test_futures]
    
    # Verify split counts
    assert sum(train_counts) + sum(test_counts) == len(test_data), \
        "Parallel split access count mismatch"


def test_schema_validation(spark_session: SparkSession):
    """Test schema validation for Hive tables."""
    # Enable schema merging
    spark_session.conf.set("spark.sql.hive.convertMetastoreParquet", "true")
    spark_session.conf.set("spark.sql.parquet.mergeSchema", "true")

    try:
        # Drop table if it exists
        spark_session.sql("DROP TABLE IF EXISTS test_schema_valid")

        # Define initial schema
        initial_schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("value", DoubleType(), True),
            StructField("category", StringType(), True)
        ])

        # Create test data with initial schema
        initial_data = [(1, 1.0, "A"), (2, 2.0, "B"), (3, 3.0, "C")]
        initial_df = spark_session.createDataFrame(initial_data, initial_schema)
        initial_df.write.mode("overwrite").saveAsTable("test_schema_valid")

        # Verify initial schema matches
        stored_schema = spark_session.table("test_schema_valid").schema
        assert stored_schema == initial_schema, "Initial schema mismatch"

        # Drop table for schema evolution test
        spark_session.sql("DROP TABLE IF EXISTS test_schema_valid")

        # Test schema evolution with new schema
        evolved_schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("value", DoubleType(), True),
            StructField("category", StringType(), True),
            StructField("active", BooleanType(), True)
        ])

        # Create new data with evolved schema
        evolved_data = [(4, 4.0, "D", True), (5, 5.0, "E", False)]
        evolved_df = spark_session.createDataFrame(evolved_data, evolved_schema)
        
        # Write with explicit schema to ensure proper type handling
        evolved_df.write \
            .mode("overwrite") \
            .option("mergeSchema", "true") \
            .saveAsTable("test_schema_valid")

        # Verify evolved schema matches
        final_schema = spark_session.table("test_schema_valid").schema
        assert final_schema == evolved_schema, "Evolved schema mismatch"

        # Verify data is correctly stored
        stored_df = spark_session.table("test_schema_valid")
        stored_data = stored_df.orderBy("id").collect()
        assert len(stored_data) == 2, "Incorrect number of rows after evolution"
        
        # Verify boolean values using explicit comparison
        first_row = stored_data[0]
        second_row = stored_data[1]
        assert first_row.active == True, f"First row boolean value incorrect: {first_row.active}"
        assert second_row.active == False, f"Second row boolean value incorrect: {second_row.active}"

    finally:
        # Cleanup
        spark_session.sql("DROP TABLE IF EXISTS test_schema_valid")


def test_data_quality_checks(spark_session: SparkSession):
    """Test data quality validation for Hive tables."""
    # Generate test data with some quality issues
    test_data = [
        (1, 1.0, "A", "2023-01-01"),  # Valid record
        (2, None, "B", "2023-01-02"),  # Null value
        (3, -1.0, "C", "invalid_date"),  # Invalid value
        (4, 1.0, "", "2023-01-04"),  # Empty string
        (5, 1.0, "D", None)  # Null date
    ]
    
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("value", DoubleType(), True),
        StructField("category", StringType(), True),
        StructField("date", StringType(), True)
    ])
    
    df = spark_session.createDataFrame(test_data, schema)
    df.write.mode("overwrite").saveAsTable("test_data_quality")
    
    # Run quality checks
    quality_df = spark_session.table("test_data_quality")
    
    # Check for nulls and empty strings separately
    null_counts = {
        c: quality_df.filter(col(c).isNull()).count()
        for c in quality_df.columns
    }
    
    empty_string_counts = {
        c: quality_df.filter(col(c) == "").count()
        for c in ["category", "date"]  # Only check string columns
    }
    
    # Verify null counts
    assert null_counts["value"] == 1, "Unexpected null count in value column"
    assert null_counts["date"] == 1, "Unexpected null count in date column"
    
    # Verify empty string counts
    assert empty_string_counts["category"] == 1, "Unexpected empty string count in category column"
    assert empty_string_counts["date"] == 0, "Unexpected empty string count in date column"
    
    # Check value constraints
    invalid_values = quality_df.filter(col("value") < 0).count()
    assert invalid_values == 1, "Unexpected count of negative values"
    
    # Check date format
    invalid_dates = quality_df.filter(
        ~col("date").rlike("^\\d{4}-\\d{2}-\\d{2}$") & col("date").isNotNull()
    ).count()
    assert invalid_dates == 1, "Unexpected count of invalid dates"
    
    # Clean up
    spark_session.sql("DROP TABLE IF EXISTS test_data_quality")


def test_error_handling(spark_session: SparkSession):
    """Test error handling scenarios for Hive operations."""
    # Test table not found
    with pytest.raises(Exception) as exc_info:
        spark_session.table("nonexistent_table")
    assert "[TABLE_OR_VIEW_NOT_FOUND]" in str(exc_info.value)
    
    # Test invalid partition
    test_df = spark_session.createDataFrame([(1, "test")], ["id", "value"])
    test_df.write.mode("overwrite").saveAsTable("test_error_handling")
    
    with pytest.raises(Exception) as exc_info:
        spark_session.sql("""
            ALTER TABLE test_error_handling ADD PARTITION (invalid_partition='test')
        """)
    assert "partition" in str(exc_info.value).lower()
    
    # Test invalid schema evolution
    test_df = spark_session.createDataFrame([(1, "test")], ["id", "value"])
    test_df.write.mode("overwrite").saveAsTable("test_schema_error")
    
    # Try to append data with incompatible schema
    new_df = spark_session.createDataFrame([(1, "test", True)], ["id", "value", "active"])
    with pytest.raises(Exception) as exc_info:
        new_df.write.mode("append").saveAsTable("test_schema_error")
    assert "schema" in str(exc_info.value).lower() or "column" in str(exc_info.value).lower()
    
    # Clean up
    spark_session.sql("DROP TABLE IF EXISTS test_error_handling")
    spark_session.sql("DROP TABLE IF EXISTS test_schema_error")


def test_hive_metadata_operations(spark_session: SparkSession):
    """Test Hive metadata operations and table properties."""
    # Create test table with properties
    test_df = spark_session.createDataFrame([(1, "test")], ["id", "value"])
    test_df.write.mode("overwrite").saveAsTable("test_metadata")
    
    # Add table properties
    spark_session.sql("""
        ALTER TABLE test_metadata 
        SET TBLPROPERTIES (
            'created_by' = 'test_suite',
            'created_date' = '2024-04-04 00:00:00',
            'description' = 'Test table for metadata operations'
        )
    """)
    
    # Verify table properties
    properties = spark_session.sql("SHOW TBLPROPERTIES test_metadata").collect()
    property_dict = {row.key: row.value for row in properties}
    
    assert property_dict['created_by'] == 'test_suite'
    assert 'created_date' in property_dict
    assert property_dict['description'] == 'Test table for metadata operations'
    
    # Test table statistics by checking row count
    row_count = spark_session.table("test_metadata").count()
    assert row_count == 1, "Incorrect number of rows in table"
    
    # Test partitioning metadata
    partitioned_df = spark_session.createDataFrame(
        [(1, "A", 2023), (2, "B", 2023), (3, "C", 2024)],
        ["id", "value", "year"]
    )
    partitioned_df.write.mode("overwrite").partitionBy("year").saveAsTable("test_partitioned")
    
    # Verify partition metadata
    partitions = spark_session.sql("SHOW PARTITIONS test_partitioned").collect()
    partition_values = sorted(row.partition for row in partitions)
    
    assert len(partition_values) == 2, "Incorrect number of partitions"
    assert "year=2023" == partition_values[0], "Missing partition for 2023"
    assert "year=2024" == partition_values[1], "Missing partition for 2024"
    
    # Test partition data access
    partition_2023_count = spark_session.table("test_partitioned").filter("year = 2023").count()
    partition_2024_count = spark_session.table("test_partitioned").filter("year = 2024").count()
    
    assert partition_2023_count == 2, "Incorrect number of rows in partition 2023"
    assert partition_2024_count == 1, "Incorrect number of rows in partition 2024"
    
    # Clean up
    spark_session.sql("DROP TABLE IF EXISTS test_metadata")
    spark_session.sql("DROP TABLE IF EXISTS test_partitioned")


def test_cleanup(spark_session: SparkSession):
    """Test cleanup of Hive tables."""
    # Drop test tables
    tables_to_drop = [
        "stage5_test_features",
        "stage5_test_train",
        "stage5_test_test"
    ]
    
    for table in tables_to_drop:
        spark_session.sql(f"DROP TABLE IF EXISTS {table}")
    
    # Verify tables are dropped
    tables = spark_session.sql("SHOW TABLES").collect()
    for table in tables_to_drop:
        assert not any(row.tableName == table for row in tables), \
            f"Failed to clean up table: {table}" 