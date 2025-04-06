"""
Logging module

This module provides logging functionality.
"""


class Logger:
    """Simple logger implementation for testing."""
    
    def __init__(self, name: str = None):
        """
        Initialize logger.
        
        Args:
            name: Logger name
        """
        self.name = name or "default"
    
    def info(self, message: str) -> None:
        """
        Log info message.
        
        Args:
            message: Message to log
        """
        print(f"[INFO] {message}")
    
    def error(self, message: str) -> None:
        """
        Log error message.
        
        Args:
            message: Message to log
        """
        print(f"[ERROR] {message}")
    
    def warning(self, message: str) -> None:
        """
        Log warning message.
        
        Args:
            message: Message to log
        """
        print(f"[WARNING] {message}")


class LoggerFactory:
    """Factory for creating loggers."""
    
    def __init__(self, log_level: str = "INFO", log_format: str = None, log_file: str = None):
        """
        Initialize logger factory.
        
        Args:
            log_level: Log level
            log_format: Log format
            log_file: Log file path
        """
        self.log_level = log_level
        self.log_format = log_format
        self.log_file = log_file
    
    def get_logger(self, name: str) -> Logger:
        """
        Get a logger with the specified name.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        return Logger(name) 