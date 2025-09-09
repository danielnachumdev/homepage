import logging
import sys
from typing import Optional


class ExtraDataFormatter(logging.Formatter):
    """Custom formatter that includes extra data from log records."""

    def format(self, record: logging.LogRecord) -> str:
        # Get the base formatted message
        base_message = super().format(record)

        # Check for data in two ways:
        # 1. Direct 'data' attribute
        # 2. 'data' key inside 'extra' dict
        data = getattr(record, 'data', None)
        if data is None:
            extra = getattr(record, 'extra', None)
            if extra and isinstance(extra, dict):
                data = extra.get('data')

        if data and isinstance(data, dict):
            # Format data as key=value pairs, sorted alphabetically by key
            sorted_items = sorted(data.items())
            data_str = " | " + " | ".join([f"{k}={v}" for k, v in sorted_items])
            return base_message + data_str

        return base_message


def setup_logger(
    name: str = "homepage_backend",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger that outputs to stdout with proper formatting.

    Args:
        name: The name of the logger
        level: The logging level (default: INFO)
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler that outputs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = ExtraDataFormatter(format_string)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger


def get_logger(name: str = "homepage_backend") -> logging.Logger:
    """
    Get a logger instance. If it doesn't exist, create it with default settings.

    Args:
        name: The name of the logger

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        setup_logger(name)

    return logger


# Create default logger instance
default_logger = setup_logger()


__all__ = [
    "ExtraDataFormatter",
    "setup_logger",
    "get_logger",
    "default_logger"
]
