"""Test configuration and shared fixtures for data transformation tests."""

import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create and return a temporary directory for test data files.
    
    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        
    Returns:
        Path to temporary test data directory
    """
    test_dir = tmp_path_factory.mktemp("test_data")
    return test_dir 