"""Logging utility for consistent logging across the application.

This module provides a configurable logging setup that can be used across different stages
of the pipeline with consistent formatting and log levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union

def setup_logger(
    name: str,
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with console and optional file handlers.
    
    Args:
        name: The name of the logger
        level: The logging level (default: INFO)
        log_file: Optional path to a log file
        format_string: Optional custom format string for log messages
        
    Returns:
        logging.Logger: Configured logger instance
        
    Examples:
        >>> logger = setup_logger("my_stage", level="DEBUG", log_file="logs/stage.log")
        >>> logger.info("Processing started")
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not format_string:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 