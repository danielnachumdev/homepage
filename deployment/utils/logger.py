"""
Simple logging utility for the deployment CLI.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Setup a logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level (defaults to INFO)

    Returns:
        Configured logger instance
    """
    if level is None:
        level = logging.INFO

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter with filename and line number
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


__all__ = [
    'setup_logger'
]
