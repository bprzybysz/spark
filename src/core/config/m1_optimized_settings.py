"""
M1 Max optimized settings module.

This module provides optimized configuration settings for Apple Silicon M1 Max
with 64GB of memory.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field

class M1SparkSettings(BaseModel):
    """Optimized Spark configuration for M1 Max."""
    
    master: str = Field(default="local[10]")  # Utilizing 10 cores for parallel processing
    app_name: str = Field(default="SparkETLMLPipeline-M1")
    executor_memory: str = Field(default="48g")  # Allocating majority of available RAM
    driver_memory: str = Field(default="8g")  # Reserved for driver
    executor_cores: int = Field(default=8)  # Optimal core allocation for M1 Max
    local_dir: str = Field(default="/tmp/spark-local-m1")
    warehouse_dir: str = Field(default="/tmp/spark-warehouse-m1")
    
    # M1-specific optimizations
    extra_java_options: str = Field(
        default="-Xss4M -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions "
        "-XX:G1NewSizePercent=40 -XX:G1MaxNewSizePercent=60 "
        "-XX:G1HeapRegionSize=32M -XX:G1ReservePercent=15"
    )
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert settings to a dict for Spark configuration."""
        return {
            "spark.master": self.master,
            "spark.app.name": self.app_name,
            "spark.executor.memory": self.executor_memory,
            "spark.driver.memory": self.driver_memory,
            "spark.executor.cores": str(self.executor_cores),
            "spark.local.dir": self.local_dir,
            "spark.sql.warehouse.dir": self.warehouse_dir,
            "spark.driver.extraJavaOptions": self.extra_java_options,
            "spark.executor.extraJavaOptions": self.extra_java_options,
            # Apple Silicon specific optimizations
            "spark.driver.extraLibraryPath": "/opt/homebrew/opt/libomp/lib",
            "spark.executor.extraLibraryPath": "/opt/homebrew/opt/libomp/lib",
            # Memory optimizations
            "spark.memory.fraction": "0.8",
            "spark.memory.storageFraction": "0.3",
            "spark.sql.shuffle.partitions": "20",
            "spark.default.parallelism": "20",
            # I/O optimizations
            "spark.sql.files.maxPartitionBytes": "134217728",
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            # Network optimizations
            "spark.network.timeout": "800s",
            "spark.executor.heartbeatInterval": "60s",
        }


class M1MLSettings(BaseModel):
    """Optimized ML settings for M1 Max."""
    
    model_dir: str = Field(default="./models")
    training_data_path: str = Field(default="./data/training")
    batch_size: int = Field(default=256)  # Larger batch size for M1 Max
    epochs: int = Field(default=10)
    learning_rate: float = Field(default=0.001)
    
    # TensorFlow specific optimizations
    tf_config: Dict[str, Any] = Field(
        default={
            "intra_op_parallelism_threads": 8,
            "inter_op_parallelism_threads": 8,
            "enable_metal": True,
            "metal_device_index": 0,
            "allow_growth": True,
            "gpu_memory_fraction": 0.8,
        }
    ) 