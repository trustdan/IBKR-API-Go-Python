"""
Logging utility for IBKR Auto Vertical Spread Trader.
"""

import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from ..config.config import config

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if available
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
            
        return json.dumps(log_obj)


def setup_logger(name: str = "ibkr_trader", log_level: Optional[str] = None) -> logging.Logger:
    """
    Setup application logger with both console and file handlers.
    
    Args:
        name: Logger name
        log_level: Log level (DEBUG, INFO, etc.), if None uses config
        
    Returns:
        Configured Logger instance
    """
    # Get log level from config if not provided
    if log_level is None:
        log_level = config.get("logging.level", "INFO")
        
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_format = config.get(
        "logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if configured
    log_file = config.get("logging.file")
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        max_size = int(config.get("logging.max_size_mb", 10)) * 1024 * 1024
        backup_count = int(config.get("logging.backup_count", 5))
        
        # Setup rotating file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level))
        
        # Use JSON formatter for file logs
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        
    return logger


# Create a default logger
logger = setup_logger()


def log_debug(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log debug message with optional extra fields."""
    logger.debug(message, extra={"extra": extra} if extra else None)


def log_info(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log info message with optional extra fields."""
    logger.info(message, extra={"extra": extra} if extra else None)


def log_warning(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log warning message with optional extra fields."""
    logger.warning(message, extra={"extra": extra} if extra else None)


def log_error(message: str, error: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log error message with optional error details and extra fields."""
    extra_dict = {"error": error} if error else {}
    if extra:
        extra_dict.update(extra)
    logger.error(message, extra={"extra": extra_dict} if extra_dict else None) 