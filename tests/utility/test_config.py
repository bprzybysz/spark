"""Tests for the configuration utility module."""

from pathlib import Path
import pytest
from pydantic import BaseModel
from src.utility.config import (
    load_config,
    get_stage_config,
    ConfigurationError
)

class TestConfig(BaseModel):
    """Sample configuration schema for testing."""
    name: str
    value: int
    optional: str = "default"

def test_load_config_basic(temp_config_dir: Path):
    """Test basic configuration loading.
    
    Args:
        temp_config_dir: Fixture providing temporary config directory
    """
    config_file = temp_config_dir / "test.yaml"
    test_config = {"name": "test", "value": 42}
    
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)
    
    loaded = load_config(config_file)
    assert loaded == test_config

def test_load_config_with_validation(temp_config_dir: Path):
    """Test configuration loading with schema validation.
    
    Args:
        temp_config_dir: Fixture providing temporary config directory
    """
    config_file = temp_config_dir / "test.yaml"
    test_config = {"name": "test", "value": 42}
    
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)
    
    loaded = load_config(config_file, TestConfig)
    assert loaded["name"] == "test"
    assert loaded["value"] == 42
    assert loaded["optional"] == "default"

def test_load_config_validation_error(temp_config_dir: Path):
    """Test configuration validation failure.
    
    Args:
        temp_config_dir: Fixture providing temporary config directory
    """
    config_file = temp_config_dir / "test.yaml"
    invalid_config = {"name": "test"}  # Missing required 'value' field
    
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(invalid_config, f)
    
    with pytest.raises(ConfigurationError):
        load_config(config_file, TestConfig)

def test_load_config_missing_file():
    """Test handling of missing configuration file."""
    with pytest.raises(ConfigurationError):
        load_config("nonexistent.yaml")

def test_get_stage_config(temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch):
    """Test stage-specific configuration loading.
    
    Args:
        temp_config_dir: Fixture providing temporary config directory
        monkeypatch: Pytest's monkeypatch fixture
    """
    # Set up test environment
    monkeypatch.setenv("CONFIG_PATH", str(temp_config_dir))
    
    # Create test config
    stage_config = {"name": "stage1", "value": 42}
    config_file = temp_config_dir / "stage1.yaml"
    
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(stage_config, f)
    
    # Test loading
    loaded = get_stage_config("stage1")
    assert loaded == stage_config
    
    # Test with schema
    loaded = get_stage_config("stage1", schema_model=TestConfig)
    assert loaded["name"] == "stage1"
    assert loaded["value"] == 42 