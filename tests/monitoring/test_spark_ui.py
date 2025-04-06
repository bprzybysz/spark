"""
Test script for demonstrating Spark UI functionality.

This script demonstrates how to use the monitoring utilities to enable
and interact with the Spark UI for monitoring Spark applications.
"""

import os
import time
import random
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, rand, explode, lit, array
import pandas as pd
import numpy as np

from src.utility.monitoring import enable_spark_ui, get_spark_ui_config, find_available_port
from src.data.spark.session import SparkSessionFactory


def generate_test_data(spark: SparkSession, rows: int = 100000, partitions: int = 10) -> DataFrame:
    """
    Generate test data for Spark UI demonstration.
    
    Args:
        spark: SparkSession
        rows: Number of rows to generate
        partitions: Number of partitions to use
        
    Returns:
        DataFrame: Generated test data
    """
    print(f"Generating test data with {rows} rows and {partitions} partitions...")
    
    # Create a pandas DataFrame with random data
    pdf = pd.DataFrame({
        'id': range(1, rows + 1),
        'value1': np.random.randn(rows),
        'value2': np.random.randn(rows),
        'category': np.random.choice(['A', 'B', 'C', 'D'], size=rows),
        'year': np.random.choice(range(2020, 2024), size=rows),
        'month': np.random.choice(range(1, 13), size=rows),
        'timestamp': pd.date_range(start='2023-01-01', periods=rows, freq='s')
    })
    
    # Convert to Spark DataFrame
    df = spark.createDataFrame(pdf)
    
    # Repartition to desired number of partitions
    return df.repartition(partitions)


def run_demo_query_operations(spark: SparkSession, df: DataFrame) -> None:
    """
    Run various Spark operations to demonstrate Spark UI's job tracking.
    
    Args:
        spark: SparkSession
        df: Input DataFrame
    """
    print("\n=== Running demonstration queries... ===")
    
    # Register as temp view for SQL
    df.createOrReplaceTempView("test_data")
    
    # Run a series of operations to create various Spark jobs
    operations = [
        # Demonstrate Hive metadata and objects
        lambda: {
            print("\n=== Exploring Hive Metadata and Storage ==="),
            print("\n>> Available Databases:"),
            spark.sql("SHOW DATABASES").show(),
            
            print("\n>> Creating a new database:"),
            spark.sql("CREATE DATABASE IF NOT EXISTS demo_db COMMENT 'Database for Spark UI demo'"),
            spark.sql("USE demo_db"),
            print("\n>> Current Database:"),
            spark.sql("SELECT current_database()").show(),
            
            print("\n>> Creating tables in demo_db:"),
            # Create a partitioned managed table
            print("\n>> Creating partitioned table by year and month..."),
            df.write.mode("overwrite") \
              .partitionBy("year", "month") \
              .format("parquet") \
              .saveAsTable("demo_partitioned_table"),
            
            # Create a bucketed table
            print("\n>> Creating bucketed table by category..."),
            df.write.mode("overwrite") \
              .bucketBy(4, "category") \
              .sortBy("id") \
              .saveAsTable("demo_bucketed_table"),
            
            print("\n>> All Tables in demo_db:"),
            spark.sql("SHOW TABLES").show(),
            
            print("\n>> Detailed Table Information:"),
            spark.sql("DESCRIBE EXTENDED demo_partitioned_table").show(truncate=False),
            
            print("\n>> Table Partitions:"),
            spark.sql("SHOW PARTITIONS demo_partitioned_table").show(),
            
            print("\n>> Storage Information:"),
            print("Table Location:", spark.sql("DESCRIBE EXTENDED demo_partitioned_table")
                  .filter("col_name = 'Location'")
                  .select("data_type").collect()[0][0]),
            
            # Show data distribution across partitions
            print("\n>> Data Distribution Across Partitions:"),
            spark.sql("""
                SELECT year, month, COUNT(*) as record_count,
                       COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
                FROM demo_partitioned_table
                GROUP BY year, month
                ORDER BY year, month
            """).show(),
            
            # Show storage format and statistics
            print("\n>> Storage Format and Statistics:"),
            spark.sql("""
                SELECT 
                    year,
                    month,
                    COUNT(*) as num_records,
                    COUNT(DISTINCT category) as unique_categories,
                    MIN(timestamp) as min_timestamp,
                    MAX(timestamp) as max_timestamp
                FROM demo_partitioned_table
                GROUP BY year, month
                ORDER BY year, month
            """).show(truncate=False),
            
            print("\n>> Analyzing table for detailed statistics..."),
            spark.sql("ANALYZE TABLE demo_partitioned_table COMPUTE STATISTICS FOR ALL COLUMNS"),
            
            print("\n>> Column Statistics:"),
            spark.sql("DESCRIBE EXTENDED demo_partitioned_table value1").show(truncate=False),
            
            print("\n>> Sample queries on partitioned data:"),
            # Query specific partitions
            spark.sql("""
                SELECT year, month, category, COUNT(*) as count
                FROM demo_partitioned_table
                WHERE year = 2023 AND month = 1
                GROUP BY year, month, category
                ORDER BY category
            """).show(),
            
            print("\n>> Cleaning up:"),
            spark.sql("DROP TABLE IF EXISTS demo_partitioned_table"),
            spark.sql("DROP TABLE IF EXISTS demo_bucketed_table"),
            spark.sql("DROP DATABASE IF EXISTS demo_db CASCADE")
        }
    ]
    
    # Execute operations with delay to allow monitoring in UI
    for i, operation in enumerate(operations, 1):
        print(f"\n>> Operation {i}/{len(operations)}")
        operation()
        time.sleep(2)  # Pause to see each job in the UI


def main():
    """Main function to demonstrate Spark UI."""
    try:
        # Find an available port
        port = find_available_port(4040)
        if not port:
            print("❌ No available ports found between 4040-4050")
            return
        
        # Create event log directory
        event_log_dir = os.path.join(os.getcwd(), "spark-events")
        os.makedirs(event_log_dir, exist_ok=True)
        
        # Create a SparkSession with UI enabled and Hive support
        print("\n=== Creating Spark session with UI and Hive enabled... ===")
        ui_config = get_spark_ui_config(port=port)
        
        # Add Hive-specific configurations
        warehouse_dir = os.path.join(os.getcwd(), "spark-warehouse")
        os.makedirs(warehouse_dir, exist_ok=True)
        
        ui_config.update({
            "spark.sql.catalogImplementation": "hive",
            "spark.sql.warehouse.dir": warehouse_dir,
            "spark.hadoop.javax.jdo.option.ConnectionURL": f"jdbc:derby:;databaseName={warehouse_dir}/metastore_db;create=true",
            "spark.hadoop.datanucleus.schema.autoCreateAll": "true",
            "spark.hadoop.hive.metastore.schema.verification": "false",
            # Hive optimizations
            "spark.sql.hive.metastorePartitionPruning": "true",
            "spark.sql.hive.convertMetastoreParquet": "true",
            "spark.sql.hive.filesourcePartitionFileCacheSize": "250000000"
        })
        
        factory = SparkSessionFactory(
            app_name="SparkUIDemo",
            master="local[*]",
            config=ui_config,
            enable_hive=True
        )
        
        spark = factory.create_session()
        
        # Verify Hive support
        catalog_impl = spark.conf.get("spark.sql.catalogImplementation")
        print(f"\nCatalog Implementation: {catalog_impl}")
        print(f"Warehouse Dir: {spark.conf.get('spark.sql.warehouse.dir')}")
        print(f"Hive Support: {'Yes' if catalog_impl == 'hive' else 'No'}")
        
        # Enable Spark UI (this checks if the UI is accessible)
        if not enable_spark_ui(spark, port=port, auto_open=True):
            print("⚠️  Warning: Spark UI might not be accessible.")
            print("     Try accessing it manually at: http://localhost:" + str(port))
        
        print("\n=== Spark UI should now be open in your browser ===")
        print(f"If not, manually open: http://localhost:{port}")
        print("Keep this terminal open while exploring the UI")
        
        # Generate test data
        df = generate_test_data(spark, rows=50000)
        
        # Run various operations to demonstrate the UI
        run_demo_query_operations(spark, df)
        
        # Keep session alive to give user time to explore UI
        print("\n=== Demo operations completed ===")
        print(f"Spark UI is available at http://localhost:{port}")
        print("Press Ctrl+C to exit when done exploring the UI")
        
        # Keep the script running until user interrupts
        while True:
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n=== Demo ended by user. Stopping Spark session... ===")
    finally:
        # Clean up
        if 'spark' in locals():
            spark.stop()
        print("\n=== Spark session stopped ===")


if __name__ == "__main__":
    main() 