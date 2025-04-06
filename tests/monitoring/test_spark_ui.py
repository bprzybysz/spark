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
        'timestamp': pd.date_range(start='2023-01-01', periods=rows, freq='S')
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
        # Simple aggregation
        lambda: df.groupBy("category").count().show(),
        
        # Window function
        lambda: df.selectExpr(
            "id", "value1", "value2",
            "avg(value1) over (partition by category) as avg_by_category"
        ).show(5),
        
        # Join operation
        lambda: df.alias("a").join(
            df.alias("b").select(col("id").alias("id_b"), col("value1").alias("value1_b")),
            col("id") == col("id_b"), "inner"
        ).show(5),
        
        # Spark SQL
        lambda: spark.sql("""
            SELECT category, 
                   COUNT(*) as count, 
                   AVG(value1) as avg_value,
                   MIN(value1) as min_value,
                   MAX(value1) as max_value
            FROM test_data
            GROUP BY category
            ORDER BY count DESC
        """).show(),
        
        # Create a complex dataset with explode
        lambda: df.select(
            "id", "category",
            explode(array([lit(x) for x in range(10)])).alias("exploded_val")
        ).groupBy("category").count().show(),
        
        # Save to parquet and read back
        lambda: {
            df.write.mode("overwrite").parquet("/tmp/spark_demo_data"),
            spark.read.parquet("/tmp/spark_demo_data").groupBy("category").count().show()
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
        
        # Create a SparkSession with UI enabled
        print("\n=== Creating Spark session with UI enabled... ===")
        ui_config = get_spark_ui_config(port=port)
        
        factory = SparkSessionFactory(
            app_name="SparkUIDemo",
            master="local[*]",
            config=ui_config,
            enable_hive=True
        )
        
        spark = factory.create_session()
        
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