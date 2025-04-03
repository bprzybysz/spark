"""Tests for the logging utility module."""

import logging
from pathlib import Path
import pytest
from src.utility.logging import setup_logger

def test_setup_logger_basic():
    """Test basic logger setup with default parameters."""
    logger = setup_logger("test_logger")
    
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)

def test_setup_logger_with_file(tmp_path: Path):
    """Test logger setup with file output.
    
    Args:
        tmp_path: Pytest fixture providing temporary directory
    """
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", log_file=log_file)
    
    assert len(logger.handlers) == 2
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    
    # Test logging
    test_message = "Test log message"
    logger.info(test_message)
    
    # Verify message in file
    assert log_file.exists()
    content = log_file.read_text()
    assert test_message in content

def test_setup_logger_custom_level():
    """Test logger setup with custom log level."""
    logger = setup_logger("test_logger", level="DEBUG")
    assert logger.level == logging.DEBUG
    
    logger = setup_logger("test_logger2", level=logging.ERROR)
    assert logger.level == logging.ERROR

def test_setup_logger_custom_format():
    """Test logger setup with custom format string."""
    format_string = "%(levelname)s - %(message)s"
    logger = setup_logger("test_logger", format_string=format_string)
    
    formatter = logger.handlers[0].formatter
    assert formatter._fmt == format_string  # type: ignore 