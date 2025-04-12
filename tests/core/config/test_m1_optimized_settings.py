"""Tests for M1-optimized Spark settings."""

import pytest
import psutil
from src.core.config.m1_optimized_settings import M1SparkSettings

@pytest.fixture
def m1_settings():
    """Create M1SparkSettings instance for testing."""
    return M1SparkSettings()

def test_memory_settings(m1_settings):
    """Test that memory settings are correctly calculated based on system memory."""
    total_mem = psutil.virtual_memory().total
    total_mem_gb = total_mem / (1024 ** 3)
    expected_executor_mem = int(total_mem_gb * 0.8)
    
    config = m1_settings.as_dict()
    assert config["spark.driver.memory"] == f"{expected_executor_mem}g"
    assert config["spark.executor.memory"] == f"{expected_executor_mem}g"
    assert abs(float(config["spark.memory.fraction"]) - 0.9) < 1e-10  # 0.6 + 0.3
    assert abs(float(config["spark.memory.storageFraction"]) - (0.6 / 0.9)) < 1e-10

def test_cpu_settings(m1_settings):
    """Test that CPU-related settings are correctly set based on system cores."""
    cpu_count = psutil.cpu_count(logical=True)
    config = m1_settings.as_dict()
    
    assert int(config["spark.driver.cores"]) == cpu_count
    assert int(config["spark.executor.cores"]) == cpu_count
    assert int(config["spark.default.parallelism"]) == cpu_count * 2
    assert int(config["spark.sql.shuffle.partitions"]) == cpu_count * 2

def test_optimization_settings(m1_settings):
    """Test that performance optimization settings are enabled."""
    config = m1_settings.as_dict()
    
    # Serialization and compression
    assert config["spark.serializer"] == "org.apache.spark.serializer.KryoSerializer"
    assert config["spark.rdd.compress"] == "true"
    assert config["spark.shuffle.compress"] == "true"
    
    # SQL optimizations
    assert config["spark.sql.adaptive.enabled"] == "true"
    assert config["spark.sql.adaptive.coalescePartitions.enabled"] == "true"
    assert config["spark.sql.adaptive.skewJoin.enabled"] == "true"
    assert config["spark.sql.tungsten.enabled"] == "true"
    assert config["spark.sql.execution.arrow.pyspark.enabled"] == "true"

def test_memory_management(m1_settings):
    """Test memory management settings."""
    config = m1_settings.as_dict()
    
    assert config["spark.memory.offHeap.enabled"] == "true"
    assert config["spark.memory.offHeap.size"] == "2g"
    assert "spark.cleaner.periodicGC.interval" in config

def test_network_timeouts(m1_settings):
    """Test that network timeouts are set to reasonable values."""
    config = m1_settings.as_dict()
    
    assert config["spark.network.timeout"] == "800s"
    assert config["spark.files.fetchTimeout"] == "120s"
    assert int(config["spark.storage.blockManagerSlaveTimeoutMs"]) >= 300000

def test_local_mode_settings(m1_settings):
    """Test settings specific to local mode execution."""
    config = m1_settings.as_dict()
    
    assert config["spark.shuffle.service.enabled"] == "false"
    assert config["spark.task.cpus"] == "1" 