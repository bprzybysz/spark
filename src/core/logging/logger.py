"""
Logging configuration module.

This module provides a factory for creating loggers with consistent configuration.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

class LoggerFactory:
    """Factory for creating loggers with consistent configuration."""
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_file: Optional[str] = None,
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
    ):
        """
        Initialize the logger factory.
        
        Args:
            log_level: The logging level
            log_format: The format string for the logger
            log_file: Optional path to a log file
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
        """
        self.log_level = self._parse_log_level(log_level)
        self.log_format = log_format
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
    
    def _parse_log_level(self, log_level: Union[str, int]) -> int:
        """
        Parse log level from string to logging level constant.
        
        Args:
            log_level: Log level as string or int
            
        Returns:
            int: Logging level constant
        """
        if isinstance(log_level, int):
            return log_level
            
        levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }
        
        return levels.get(log_level.upper(), logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: The name for the logger, typically the module name
            
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # If the logger is already configured, return it
        if logger.handlers:
            return logger
            
        logger.setLevel(self.log_level)
        logger.propagate = False
        
        # Create formatter
        formatter = logging.Formatter(self.log_format)
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Add file handler if log file is specified
        if self.log_file:
            log_file_path = Path(self.log_file)
            
            # Ensure the directory exists
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                filename=str(log_file_path),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger 