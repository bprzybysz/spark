"""Tests for M1-optimized settings configuration."""

import pytest
import os
from src.core.config.settings import Settings
from src.core.config.m1_optimized_settings import M1SparkSettings, M1MLSettings


def test_default_profile():
    """Test default profile settings."""
    settings = Settings()
    assert settings.profile == "default"
    assert settings.spark.executor_memory == "4g"
    assert settings.spark.driver_memory == "2g"
    assert settings.ml.batch_size == 64


def test_dev_profile():
    """Test M1-optimized dev profile settings."""
    os.environ["PROFILE"] = "dev"
    settings = Settings()
    
    # Test Spark settings
    assert isinstance(settings.spark, M1SparkSettings)
    assert settings.spark.executor_memory == "48g"
    assert settings.spark.driver_memory == "8g"
    assert settings.spark.executor_cores == 8
    assert "UseG1GC" in settings.spark.extra_java_options
    
    # Test ML settings
    assert isinstance(settings.ml, M1MLSettings)
    assert settings.ml.batch_size == 256
    assert settings.ml.tf_config["enable_metal"] is True
    assert settings.ml.tf_config["intra_op_parallelism_threads"] == 8
    
    # Test Spark configuration dictionary
    spark_config = settings.spark.as_dict()
    assert spark_config["spark.memory.fraction"] == "0.8"
    assert spark_config["spark.sql.adaptive.enabled"] == "true"
    assert spark_config["spark.driver.extraLibraryPath"] == "/opt/homebrew/opt/libomp/lib"
    
    # Clean up
    del os.environ["PROFILE"]


def test_m1_spark_settings():
    """Test M1SparkSettings configuration."""
    settings = M1SparkSettings()
    config_dict = settings.as_dict()
    
    assert config_dict["spark.master"] == "local[10]"
    assert config_dict["spark.executor.memory"] == "48g"
    assert config_dict["spark.sql.adaptive.coalescePartitions.enabled"] == "true"
    assert config_dict["spark.network.timeout"] == "800s"


def test_m1_ml_settings():
    """Test M1MLSettings configuration."""
    settings = M1MLSettings()
    
    assert settings.batch_size == 256
    assert settings.tf_config["enable_metal"] is True
    assert settings.tf_config["gpu_memory_fraction"] == 0.8
    assert settings.tf_config["metal_device_index"] == 0 