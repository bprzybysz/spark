"""
M1 Max optimized settings module.

This module provides optimized configuration settings for Apple Silicon M1 Max
with 64GB of memory.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field
import psutil

class M1SparkSettings(BaseModel):
    """Optimized Spark configuration for M1 Max."""
    
    def __init__(self, **kwargs):
        # Get system info
        cpu_count = psutil.cpu_count(logical=True)
        total_mem = psutil.virtual_memory().total
        total_mem_gb = total_mem / (1024 ** 3)
        
        # Set dynamic defaults
        kwargs.setdefault("master", f"local[{cpu_count}]")
        kwargs.setdefault("app_name", "SparkETLMLPipeline-M1")
        kwargs.setdefault("executor_cores", cpu_count)
        kwargs.setdefault("local_dir", "/tmp/spark-local-m1")
        kwargs.setdefault("warehouse_dir", "/tmp/spark-warehouse-m1")
        
        super().__init__(**kwargs)
        
        # Initialize config dictionary
        self._config = {}
        
        # Calculate optimal memory fractions
        executor_mem_fraction = 0.85  # Reserve 15% for system
        storage_mem_fraction = 0.6   # 60% of executor memory for storage
        shuffle_mem_fraction = 0.3   # 30% of executor memory for shuffle
        
        # Calculate memory sizes
        executor_mem = int(total_mem_gb * executor_mem_fraction)
        
        # Update config with optimized settings
        self._config.update({
            # Memory configuration
            "spark.driver.memory": f"{executor_mem}g",
            "spark.executor.memory": f"{executor_mem}g",
            "spark.memory.fraction": str(storage_mem_fraction + shuffle_mem_fraction),
            "spark.memory.storageFraction": str(storage_mem_fraction / (storage_mem_fraction + shuffle_mem_fraction)),
            
            # CPU configuration
            "spark.driver.cores": str(cpu_count),
            "spark.executor.cores": str(cpu_count),
            "spark.default.parallelism": str(cpu_count * 4),  # Increased parallelism
            "spark.task.cpus": "1",
            "spark.task.maxFailures": "4",  # Increased failure tolerance
            
            # Shuffle configuration
            "spark.shuffle.file.buffer": "2m",  # Increased buffer size
            "spark.shuffle.unsafe.file.output.buffer": "2m",
            "spark.shuffle.service.enabled": "false",
            "spark.shuffle.compress": "true",
            "spark.shuffle.spill.compress": "true",
            "spark.shuffle.io.maxRetries": "6",  # Increased retry attempts
            "spark.shuffle.io.retryWait": "10s",  # Increased retry wait time
            
            # Network configuration
            "spark.network.timeout": "1200s",  # Increased timeout
            "spark.executor.heartbeatInterval": "30s",  # Reduced heartbeat interval
            "spark.storage.blockManagerSlaveTimeoutMs": "300000",
            "spark.network.maxRetries": "5",  # Increased network retries
            "spark.locality.wait": "5s",  # Reduced locality wait
            
            # SQL configuration
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.localShuffleReader.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.sql.shuffle.partitions": str(cpu_count * 4),
            "spark.sql.files.maxPartitionBytes": "256m",  # Increased partition size
            "spark.sql.adaptive.advisoryPartitionSizeInBytes": "256m",
            "spark.sql.tungsten.enabled": "true",
            "spark.sql.execution.arrow.pyspark.enabled": "true",
            "spark.sql.execution.arrow.maxRecordsPerBatch": "10000",  # Optimized batch size
            "spark.sql.execution.arrow.fallback.enabled": "true",
            
            # Memory management
            "spark.memory.offHeap.enabled": "true",
            "spark.memory.offHeap.size": "2g",
            "spark.cleaner.periodicGC.interval": "30min",
            "spark.cleaner.referenceTracking": "true",
            "spark.cleaner.referenceTracking.blocking": "true",
            "spark.cleaner.referenceTracking.cleanCheckpoints": "true",
            
            # Serialization
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.kryoserializer.buffer.max": "2g",  # Increased buffer size
            "spark.rdd.compress": "true",
            
            # Driver configuration
            "spark.driver.extraJavaOptions": self.extra_java_options,
            "spark.driver.extraLibraryPath": "/opt/homebrew/opt/libomp/lib",
            "spark.driver.maxResultSize": "4g",  # Increased result size limit
            
            # Basic settings
            "spark.master": self.master,
            "spark.app.name": self.app_name,
            "spark.local.dir": self.local_dir,
            "spark.sql.warehouse.dir": self.warehouse_dir,
            
            # RPC settings
            "spark.rpc.message.maxSize": "1024",
            "spark.rpc.askTimeout": "600s",
            "spark.rpc.lookupTimeout": "120s",
            
            # Speculation settings
            "spark.speculation": "true",
            "spark.speculation.interval": "1000ms",
            "spark.speculation.multiplier": "2",
            "spark.speculation.quantile": "0.75"
        })
    
    master: str = Field(default="local[*]")  # Will be set dynamically in __init__
    app_name: str = Field(default="SparkETLMLPipeline-M1")
    executor_cores: int = Field(default=None)  # Will be set dynamically in __init__
    local_dir: str = Field(default="/tmp/spark-local-m1")
    warehouse_dir: str = Field(default="/tmp/spark-warehouse-m1")
    
    # M1-specific optimizations
    extra_java_options: str = Field(
        default="-Xss4M -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions "
        "-XX:G1NewSizePercent=40 -XX:G1MaxNewSizePercent=60 "
        "-XX:G1HeapRegionSize=32M -XX:G1ReservePercent=15 "
        "-XX:+UseCompressedOops -XX:+UseCompressedClassPointers "
        "-XX:+OptimizeStringConcat -XX:+UseStringDeduplication"
    )
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert settings to a dict for Spark configuration."""
        return self._config


class M1MLSettings(BaseModel):
    """Optimized ML settings for M1 Max."""
    
    model_dir: str = Field(default="./models")
    training_data_path: str = Field(default="./data/training")
    batch_size: int = Field(default=512)  # Increased for better M1 performance
    epochs: int = Field(default=10)
    learning_rate: float = Field(default=0.001)
    
    # TensorFlow specific optimizations
    tf_config: Dict[str, Any] = Field(
        default={
            "intra_op_parallelism_threads": 10,  # Match physical cores
            "inter_op_parallelism_threads": 10,  # Match physical cores
            "enable_metal": True,
            "metal_device_index": 0,
            "allow_growth": True,
            "gpu_memory_fraction": 0.9,  # Increased memory allocation
            "mixed_precision": True,  # Enable mixed precision for better performance
            "xla_jit": True,  # Enable XLA JIT compilation
            "layout_optimizer": True,  # Enable layout optimization
            "constant_folding": True,  # Enable constant folding
            "shape_optimization": True,  # Enable shape optimization
            "remapping": True,  # Enable operation remapping
            "arithmetic_optimization": True,  # Enable arithmetic optimizations
            "dependency_optimization": True,  # Enable dependency optimizations
            "loop_optimization": True,  # Enable loop optimizations
            "function_optimization": True,  # Enable function optimizations
            "debug_stripper": True,  # Strip debug operations
            "scoped_allocator_optimization": True,  # Enable scoped allocator optimization
            "pin_to_host_optimization": True,  # Enable pin to host optimization
            "implementation_selector": True,  # Enable implementation selector
            "auto_mixed_precision": True,  # Enable automatic mixed precision
            "disable_meta_optimizer": False,  # Enable meta optimizer
            "min_graph_nodes": 1,  # Minimum number of nodes to enable optimizations
            "meta_optimizer_iterations": "aggressive",  # Aggressive optimization
            "memory_optimization": "heuristics",  # Enable memory optimization
        }
    ) 