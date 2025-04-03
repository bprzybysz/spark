"""Utility functions for Spark session management and configuration."""

import os
from typing import Dict, Any

from pyspark.sql import SparkSession


def create_spark_session(config: Dict[str, Any]) -> SparkSession:
    """Create a Spark session with the given configuration.
    
    Args:
        config: Dictionary of Spark configuration options
        
    Returns:
        Configured SparkSession
    """
    # Set Python environment variables
    os.environ["PYSPARK_PYTHON"] = os.environ.get("PYSPARK_PYTHON", "python3")
    os.environ["PYSPARK_DRIVER_PYTHON"] = os.environ.get("PYSPARK_DRIVER_PYTHON", "python3")
    
    # Create builder with base configuration
    builder = SparkSession.builder
    
    # Apply all configuration options
    for key, value in config.items():
        builder = builder.config(key, value)
    
    # Enable Hive support if warehouse directory is set
    if "spark.sql.warehouse.dir" in config:
        builder = builder.enableHiveSupport()
    
    return builder.getOrCreate()


def cleanup_spark_session(spark: SparkSession) -> None:
    """Clean up Spark session and temporary files.
    
    Args:
        spark: SparkSession to clean up
    """
    # Stop Spark session
    if spark is not None:
        spark.stop()
    
    # Clean up temporary directories
    temp_dirs = [
        os.environ.get("SPARK_LOCAL_DIRS", "/tmp"),
        os.environ.get("SPARK_WORKER_DIR", "/tmp"),
        os.environ.get("SPARK_WAREHOUSE_DIR", "/tmp/hive/warehouse")
    ]
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for name in files:
                        if name.startswith("spark-"):
                            os.remove(os.path.join(root, name))
                    for name in dirs:
                        if name.startswith("spark-"):
                            os.rmdir(os.path.join(root, name))
            except Exception as e:
                print(f"Warning: Failed to clean up {temp_dir}: {e}")


def configure_spark_memory(spark: SparkSession, memory_fraction: float = 0.8) -> None:
    """Configure Spark memory settings for optimal performance.
    
    Args:
        spark: SparkSession to configure
        memory_fraction: Fraction of memory to use for storage (default: 0.8)
    """
    # Set memory fraction
    spark.conf.set("spark.memory.fraction", str(memory_fraction))
    spark.conf.set("spark.memory.storageFraction", str(memory_fraction * 0.5))
    
    # Enable off-heap memory
    spark.conf.set("spark.memory.offHeap.enabled", "true")
    spark.conf.set("spark.memory.offHeap.size", "2g")
    
    # Set shuffle settings
    spark.conf.set("spark.shuffle.file.buffer", "1m")
    spark.conf.set("spark.shuffle.spill.compress", "true")
    spark.conf.set("spark.shuffle.compress", "true")
    
    # Set broadcast settings
    spark.conf.set("spark.broadcast.compress", "true")
    spark.conf.set("spark.broadcast.blockSize", "4m")


def optimize_spark_execution(spark: SparkSession) -> None:
    """Optimize Spark execution settings for better performance.
    
    Args:
        spark: SparkSession to configure
    """
    # Set execution parameters
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")
    
    # Enable AQE features
    spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
    spark.conf.set("spark.sql.adaptive.nonEmptyPartitionRatioForBroadcastJoin", "0.2")
    
    # Set codegen settings
    spark.conf.set("spark.sql.codegen.wholeStage", "true")
    spark.conf.set("spark.sql.codegen.factoryMode", "CODEGEN_ONLY")
    
    # Enable vectorized reader
    spark.conf.set("spark.sql.parquet.enableVectorizedReader", "true")
    spark.conf.set("spark.sql.orc.enableVectorizedReader", "true")
    
    # Set join strategy parameters
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")
    spark.conf.set("spark.sql.shuffle.partitions", "200") 