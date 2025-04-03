"""Common test configuration and fixtures.

This module provides shared test utilities and fixtures that can be used
across different test stages.
"""

import os
from pathlib import Path
import pytest
from typing import Generator, Dict, Any

# Test data directory setup
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

@pytest.fixture
def test_data_dir() -> Path:
    """Fixture providing the test data directory path."""
    return TEST_DATA_DIR

@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture providing a temporary directory for test configurations.
    
    Args:
        tmp_path: Pytest's temporary directory fixture
        
    Yields:
        Path to temporary configuration directory
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    yield config_dir

@pytest.fixture
def sample_config(temp_config_dir: Path) -> Dict[str, Any]:
    """Fixture providing a sample configuration for testing.
    
    Args:
        temp_config_dir: Temporary configuration directory
        
    Returns:
        Dict containing sample configuration
    """
    config = {
        "name": "test_stage",
        "input_path": str(TEST_DATA_DIR / "input"),
        "output_path": str(TEST_DATA_DIR / "output"),
        "parameters": {
            "threshold": 0.5,
            "batch_size": 100
        }
    }
    
    # Create config file
    config_file = temp_config_dir / "test_stage.yaml"
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    
    return config

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch: pytest.MonkeyPatch, temp_config_dir: Path) -> None:
    """Automatically set up test environment variables.
    
    Args:
        monkeypatch: Pytest's monkeypatch fixture
        temp_config_dir: Temporary configuration directory
    """
    monkeypatch.setenv("CONFIG_PATH", str(temp_config_dir))
    monkeypatch.setenv("TEST_MODE", "true") 