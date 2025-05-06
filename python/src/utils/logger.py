"""
Logging utility for IBKR Auto Vertical Spread Trader.
"""

import logging
import os
import sys
from datetime import datetime


# Global logger instance
_logger = None


def setup_logger(log_level: str = "INFO", log_file: str = None, console: bool = True) -> logging.Logger:
    """Set up the logger.
    
    Args:
        log_level: Logging level
        log_file: Path to log file (if None, logs to console only)
        console: Whether to log to console
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is not None:
        return _logger
        
    # Create logger
    _logger = logging.getLogger("auto_trader")
    _logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
        
    # Add file handler if log file specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)
        
    return _logger


def get_logger() -> logging.Logger:
    """Get the logger instance.
    
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logger()
        
    return _logger


def log_debug(message: str) -> None:
    """Log a debug message.
    
    Args:
        message: Message to log
    """
    logger = get_logger()
    logger.debug(message)


def log_info(message: str) -> None:
    """Log an info message.
    
    Args:
        message: Message to log
    """
    logger = get_logger()
    logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message.
    
    Args:
        message: Message to log
    """
    logger = get_logger()
    logger.warning(message)


def log_error(message: str) -> None:
    """Log an error message.
    
    Args:
        message: Message to log
    """
    logger = get_logger()
    logger.error(message)


def log_exception(message: str) -> None:
    """Log an exception message with traceback.
    
    Args:
        message: Message to log
    """
    logger = get_logger()
    logger.exception(message)


class LogCapture:
    """Context manager that captures logs for testing or processing."""
    
    def __init__(self, level: str = "INFO"):
        """Initialize log capture.
        
        Args:
            level: Minimum log level to capture
        """
        self.level = getattr(logging, level.upper())
        self.captured_logs = []
        self.handler = None
        
    def __enter__(self):
        """Set up log capture."""
        self.handler = CaptureHandler(self.captured_logs, self.level)
        logger = get_logger()
        logger.addHandler(self.handler)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up log capture."""
        if self.handler:
            logger = get_logger()
            logger.removeHandler(self.handler)
            
    def get_logs(self) -> list:
        """Get captured logs.
        
        Returns:
            List of log records
        """
        return self.captured_logs


class CaptureHandler(logging.Handler):
    """Handler that captures log records to a list."""
    
    def __init__(self, records: list, level: int):
        """Initialize capture handler.
        
        Args:
            records: List to store log records
            level: Minimum log level to capture
        """
        super().__init__(level)
        self.records = records
        
    def emit(self, record):
        """Process a log record.
        
        Args:
            record: Log record to process
        """
        self.records.append({
            'time': datetime.fromtimestamp(record.created),
            'level': record.levelname,
            'message': record.getMessage()
        }) 