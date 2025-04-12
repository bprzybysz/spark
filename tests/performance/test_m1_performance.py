"""Performance tests for M1-optimized configuration."""

import os
import sys
import time
import psutil
import numpy as np
import tensorflow as tf
from typing import Dict, Any, Union, Tuple
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
import multiprocessing
import warnings
import pyspark

from src.core.config.settings import Settings, MLSettings
from src.core.config.m1_optimized_settings import M1SparkSettings, M1MLSettings


def monitor_resources(interval: float = 0.1) -> Tuple[float, float]:
    """Monitor CPU and memory usage with higher sampling rate."""
    # Get per-CPU utilization
    cpu_percents = psutil.cpu_percent(interval=interval, percpu=True)
    memory_percent = psutil.virtual_memory().percent
    print(f"\nCPU Usage per core: {cpu_percents}")
    print(f"Average CPU Usage: {sum(cpu_percents) / len(cpu_percents):.1f}%")
    return sum(cpu_percents) / len(cpu_percents), memory_percent


def create_spark_session(config: Dict[str, Any]) -> SparkSession:
    """Create a Spark session with aggressive resource allocation and Hive support."""
    # Set Python environment variables for PySpark
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    
    # Set Spark and Hadoop local directories
    os.environ["SPARK_LOCAL_DIRS"] = "/tmp"
    warehouse_dir = "/tmp/hive/warehouse"
    os.environ["SPARK_WAREHOUSE_DIR"] = warehouse_dir
    
    # Configure Hadoop home and native libraries
    hadoop_home = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hadoop")
    os.environ["HADOOP_HOME"] = hadoop_home
    
    # Create directories if they don't exist
    os.makedirs(warehouse_dir, exist_ok=True)
    os.makedirs(hadoop_home, exist_ok=True)
    os.makedirs(os.path.join(hadoop_home, "bin"), exist_ok=True)
    
    # Create empty winutils file for compatibility
    with open(os.path.join(hadoop_home, "bin", "winutils"), "w") as f:
        pass
    os.chmod(os.path.join(hadoop_home, "bin", "winutils"), 0o755)
    
    # Set maximum resource allocation for tests
    cpu_count = psutil.cpu_count(logical=True)
    os.environ["SPARK_WORKER_CORES"] = str(cpu_count)
    os.environ["SPARK_WORKER_MEMORY"] = "48g"
    os.environ["SPARK_DRIVER_MEMORY"] = "16g"
    
    # Set local IP to avoid hostname warning
    os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
    
    builder = SparkSession.builder
    for key, value in config.items():
        builder = builder.config(key, value)
    
    # Aggressive resource configuration with Hive support
    builder = builder.config("spark.master", f"local[{cpu_count}]") \
                    .config("spark.driver.cores", str(cpu_count)) \
                    .config("spark.task.cpus", "1") \
                    .config("spark.sql.shuffle.partitions", str(cpu_count * 4)) \
                    .config("spark.default.parallelism", str(cpu_count * 4)) \
                    .config("spark.memory.fraction", "0.8") \
                    .config("spark.memory.storageFraction", "0.3") \
                    .config("spark.executor.memory", "12g") \
                    .config("spark.driver.memory", "16g") \
                    .config("spark.memory.offHeap.enabled", "true") \
                    .config("spark.memory.offHeap.size", "16g") \
                    .config("spark.sql.debug.maxToStringFields", "100") \
                    .config("spark.driver.maxResultSize", "8g") \
                    .config("spark.kryoserializer.buffer.max", "1g") \
                    .config("spark.network.timeout", "800s") \
                    .config("spark.executor.heartbeatInterval", "60s") \
                    .config("spark.eventLog.gcMetrics.youngGenerationGarbageCollectors", "G1 Young Generation") \
                    .config("spark.eventLog.gcMetrics.oldGenerationGarbageCollectors", "G1 Old Generation") \
                    .config("spark.sql.warehouse.dir", warehouse_dir) \
                    .config("spark.sql.broadcastTimeout", "600") \
                    .config("spark.sql.autoBroadcastJoinThreshold", "100m") \
                    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                    .config("spark.hadoop.javax.jdo.option.ConnectionURL", f"jdbc:derby:;databaseName={warehouse_dir}/metastore_db;create=true") \
                    .config("spark.hadoop.datanucleus.schema.autoCreateAll", "true") \
                    .config("spark.hadoop.hive.metastore.schema.verification", "false") \
                    .enableHiveSupport()
    
    return builder.appName("PerformanceTest").getOrCreate()


def optimize_tensorflow_config(settings: Union[MLSettings, M1MLSettings]) -> None:
    """Optimize TensorFlow configuration for maximum CPU/GPU utilization."""
    physical_devices = tf.config.list_physical_devices()
    print("\nAvailable TensorFlow Devices:")
    print("-" * 40)
    for device in physical_devices:
        print(f"- {device.device_type}: {device.name}")
    
    # Enable Metal GPU if available
    metal_devices = tf.config.list_physical_devices('GPU')
    if metal_devices and hasattr(settings, "tf_config") and settings.tf_config.get("enable_metal"):
        try:
            # Configure Metal device
            tf.config.experimental.set_memory_growth(metal_devices[0], True)
            tf.config.set_logical_device_configuration(
                metal_devices[0],
                [tf.config.LogicalDeviceConfiguration(memory_limit=settings.tf_config.get("gpu_memory_fraction", 0.8) * 100)]
            )
            print("\nMetal GPU enabled with memory growth and memory limit")
            
            # Set mixed precision policy for better performance
            tf.keras.mixed_precision.set_global_policy('mixed_float16')
            print("Mixed precision (float16) enabled for better GPU performance")
        except Exception as e:
            print(f"\nWarning: Could not configure Metal GPU: {e}")
    
    # Maximize thread utilization
    num_cores = psutil.cpu_count(logical=True)
    tf.config.threading.set_inter_op_parallelism_threads(num_cores)
    tf.config.threading.set_intra_op_parallelism_threads(num_cores)
    
    # Enable aggressive performance optimizations
    tf.config.optimizer.set_jit(True)  # Enable XLA
    tf.config.experimental.enable_tensor_float_32_execution(True)  # Enable TF32
    print(f"\nTensorFlow configured with {num_cores} threads for both inter and intra op parallelism")


def generate_test_data(spark: SparkSession, num_rows: int = 100000) -> Any:
    """Generate test data for performance testing using Hive tables."""
    # Smaller dataset for initial testing
    np.random.seed(42)
    num_features = 200  # Doubled features for more CPU work
    X = np.random.randn(num_rows, num_features)
    y = np.sum(X * np.random.randn(num_features), axis=1) + np.random.randn(num_rows)
    
    feature_cols = [f"feature_{i}" for i in range(num_features)]
    
    # Create initial DataFrame with features as separate columns
    rows = []
    for i in range(num_rows):
        row = {f"feature_{j}": float(X[i, j]) for j in range(num_features)}
        row["label"] = float(y[i])
        row["partition_id"] = i % 10  # Add partition column
        rows.append(row)
    
    # Create DataFrame with optimized partition size
    cpu_count = psutil.cpu_count(logical=True)
    num_partitions = cpu_count * 4  # Increased partitions for better parallelism
    
    # Create DataFrame with separate columns
    df = spark.createDataFrame(rows) \
             .repartition(num_partitions)
    
    print(f"\nCreated DataFrame with {num_partitions} partitions")
    
    # Create Hive table for better data locality
    spark.sql("DROP TABLE IF EXISTS performance_test_features")
    
    # Save to Hive with partitioning by partition_id for better parallel access
    df.write.format("parquet") \
           .mode("overwrite") \
           .partitionBy("partition_id") \
           .option("compression", "snappy") \
           .saveAsTable("performance_test_features")
    
    # Read back from Hive with optimized layout
    df = spark.table("performance_test_features")
    
    # Cache in memory and disk for better locality
    df.persist(storageLevel=pyspark.StorageLevel.MEMORY_AND_DISK)
    df.count()  # Force caching
    
    return df


def run_spark_benchmark(spark: SparkSession, df: Any) -> Tuple[float, float, float]:
    """Run Spark ML benchmark with continuous monitoring."""
    print("\nStarting Spark benchmark...")
    start_time = time.time()
    start_cpu, start_mem = monitor_resources()
    
    # Create Hive table for assembled features
    feature_cols = [f"feature_{i}" for i in range(200)]  # Updated for new feature count
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    df_assembled = assembler.transform(df)
    
    # Save assembled features to Hive for better data locality
    df_assembled.write.format("parquet") \
                     .mode("overwrite") \
                     .partitionBy("partition_id") \
                     .option("compression", "snappy") \
                     .saveAsTable("performance_test_assembled")
    
    # Read back optimized data
    df_assembled = spark.table("performance_test_assembled")
    
    # Configure Linear Regression with compute-intensive parameters
    lr = LinearRegression(
        maxIter=50,  # Increased iterations
        elasticNetParam=0.5,
        regParam=0.01,
        standardization=True,
        solver="l-bfgs",  # Changed to L-BFGS solver for more CPU intensity
        aggregationDepth=4,  # Increased aggregation depth
        maxBlockSizeInMB=128  # Increased block size
    )
    
    # Train and evaluate model with progress monitoring
    print("\nTraining Spark ML model...")
    model = lr.fit(df_assembled)
    monitor_resources()  # Check mid-training
    
    # Save predictions to Hive and force parallel execution
    predictions = model.transform(df_assembled)
    predictions.write.format("parquet") \
                    .mode("overwrite") \
                    .partitionBy("partition_id") \
                    .option("compression", "snappy") \
                    .saveAsTable("performance_test_predictions")
    
    # Force parallel computation with optimized read
    spark.table("performance_test_predictions").count()
    
    end_time = time.time()
    end_cpu, end_mem = monitor_resources()
    
    # Cleanup Hive tables
    spark.sql("DROP TABLE IF EXISTS performance_test_features")
    spark.sql("DROP TABLE IF EXISTS performance_test_assembled")
    spark.sql("DROP TABLE IF EXISTS performance_test_predictions")
    
    return end_time - start_time, (end_cpu + start_cpu) / 2, (end_mem + start_mem) / 2


def run_tensorflow_benchmark(settings: Union[MLSettings, M1MLSettings]) -> Tuple[float, float, float, Dict[str, Any]]:
    """Run TensorFlow benchmark with intensive computation and GPU monitoring."""
    optimize_tensorflow_config(settings)
    start_time = time.time()
    start_cpu, start_mem = monitor_resources()
    
    # More compute-intensive dataset with larger dimensions
    num_samples = 100000  # Doubled samples
    num_features = 8000   # Doubled features
    X = np.random.randn(num_samples, num_features).astype(np.float32)
    y = np.sum(X, axis=1, keepdims=True).astype(np.float32)
    
    # Create deeper compute-intensive model architecture
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(8192, activation='relu', kernel_initializer='glorot_uniform'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(4096, activation='relu', kernel_initializer='glorot_uniform'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(2048, activation='relu', kernel_initializer='glorot_uniform'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1024, activation='relu', kernel_initializer='glorot_uniform'),
        tf.keras.layers.Dense(1)
    ])
    
    # Configure optimizer with mixed precision
    optimizer = tf.keras.optimizers.Adam(
        learning_rate=settings.learning_rate,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-07
    )
    
    model.compile(
        optimizer=optimizer,
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=['mae'],
        jit_compile=True  # Enable XLA compilation for the model instead
    )
    
    # Train with optimized batch size and GPU monitoring
    print("\nTraining TensorFlow model...")
    batch_size = settings.batch_size
    
    # Initialize metrics storage
    metrics_history = {
        'gpu_utilization': [],
        'gpu_memory': [],
        'batch_times': [],
        'epoch_times': []
    }
    
    class GPUMonitorCallback(tf.keras.callbacks.Callback):
        def on_epoch_begin(self, epoch, logs=None):
            self.epoch_start_time = time.time()
        
        def on_epoch_end(self, epoch, logs=None):
            epoch_time = time.time() - self.epoch_start_time
            metrics_history['epoch_times'].append(epoch_time)
            
            cpu, mem = monitor_resources()
            print(f"\nEpoch {epoch + 1} Stats:")
            print(f"Time: {epoch_time:.2f}s")
            print(f"CPU Usage: {cpu:.1f}%")
            print(f"Memory: {mem:.1f}%")
            
            # Get GPU stats if available
            try:
                gpu_info = tf.config.experimental.get_memory_info('GPU:0')
                gpu_mem_used = gpu_info['peak'] / (1024 ** 3)  # Convert to GB
                metrics_history['gpu_memory'].append(gpu_mem_used)
                print(f"GPU Memory: {gpu_mem_used:.2f}GB")
            except:
                pass
        
        def on_batch_end(self, batch, logs=None):
            if batch % 50 == 0:  # Monitor every 50 batches
                metrics_history['batch_times'].append(time.time())
                cpu, _ = monitor_resources()
                metrics_history['gpu_utilization'].append(cpu)
    
    # Add early stopping to prevent unnecessary computation
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=2,
        restore_best_weights=True
    )
    
    history = model.fit(
        X, y,
        epochs=10,
        batch_size=batch_size,
        verbose=1,
        validation_split=0.2,
        callbacks=[GPUMonitorCallback(), early_stopping]
    )
    
    end_time = time.time()
    end_cpu, end_mem = monitor_resources()
    
    # Calculate performance metrics
    metrics_history.update({
        'training_time': end_time - start_time,
        'avg_epoch_time': np.mean(metrics_history['epoch_times']),
        'final_loss': history.history['loss'][-1],
        'final_val_loss': history.history['val_loss'][-1],
        'avg_gpu_utilization': np.mean(metrics_history['gpu_utilization']) if metrics_history['gpu_utilization'] else 0,
        'peak_gpu_memory': max(metrics_history['gpu_memory']) if metrics_history['gpu_memory'] else 0
    })
    
    return end_time - start_time, (end_cpu + start_cpu) / 2, (end_mem + start_mem) / 2, metrics_history


def test_performance_comparison():
    """Compare performance between default and M1-optimized configurations."""
    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    
    print("\nSystem Resources:")
    print(f"CPU Cores (Physical/Logical): {psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}")
    print(f"Memory Total: {psutil.virtual_memory().total / (1024**3):.1f}GB")
    
    # Set OpenMP and MKL thread settings for better CPU utilization
    os.environ["OMP_NUM_THREADS"] = str(psutil.cpu_count(logical=True))
    os.environ["MKL_NUM_THREADS"] = str(psutil.cpu_count(logical=True))
    
    # Test with default configuration
    print("\nRunning default configuration tests...")
    os.environ["PROFILE"] = "default"
    default_settings = Settings()
    default_spark = create_spark_session(default_settings.spark.as_dict())
    df = generate_test_data(default_spark)
    
    default_spark_time, default_spark_cpu, default_spark_mem = run_spark_benchmark(default_spark, df)
    default_tf_time, default_tf_cpu, default_tf_mem, default_tf_metrics = run_tensorflow_benchmark(default_settings.ml)
    
    default_spark.stop()
    
    # Test with M1-optimized configuration
    print("\nRunning M1-optimized configuration tests...")
    os.environ["PROFILE"] = "dev"
    m1_settings = Settings()
    m1_spark = create_spark_session(m1_settings.spark.as_dict())
    df = generate_test_data(m1_spark)
    
    m1_spark_time, m1_spark_cpu, m1_spark_mem = run_spark_benchmark(m1_spark, df)
    m1_tf_time, m1_tf_cpu, m1_tf_mem, m1_tf_metrics = run_tensorflow_benchmark(m1_settings.ml)
    
    m1_spark.stop()
    
    # Print detailed results
    print("\nPerformance Comparison Results:")
    print("-" * 60)
    print("Spark ML Pipeline:")
    print(f"  Default:      Time: {default_spark_time:.2f}s, CPU: {default_spark_cpu:.1f}%, Mem: {default_spark_mem:.1f}%")
    print(f"  M1 Optimized: Time: {m1_spark_time:.2f}s, CPU: {m1_spark_cpu:.1f}%, Mem: {m1_spark_mem:.1f}%")
    print(f"  Time Improvement: {((default_spark_time - m1_spark_time) / default_spark_time * 100):.1f}%")
    
    print("\nTensorFlow Training:")
    print(f"  Default:      Time: {default_tf_time:.2f}s, CPU: {default_tf_cpu:.1f}%, Mem: {default_tf_mem:.1f}%")
    print(f"  M1 Optimized: Time: {m1_tf_time:.2f}s, CPU: {m1_tf_cpu:.1f}%, Mem: {m1_tf_mem:.1f}%")
    print(f"  Time Improvement: {((default_tf_time - m1_tf_time) / default_tf_time * 100):.1f}%")
    
    # Assert improvements with adjusted CPU utilization thresholds
    assert m1_spark_time < default_spark_time, "M1-optimized Spark should be faster"
    assert m1_tf_time < default_tf_time, "M1-optimized TensorFlow should be faster"
    assert m1_spark_cpu > 60, "CPU utilization should be above 60%"  # Adjusted threshold
    assert m1_spark_mem > 40, "Memory utilization should be above 40%" 