"""
Simple logging utility for the deployment CLI.
"""

import logging
import sys
from typing import Optional


class DeploymentLogFilter(logging.Filter):
    """
    Custom log filter that only allows deployment-related logs unless verbose mode is enabled.
    """

    def __init__(self, verbose: bool = False):
        super().__init__()
        self.verbose = verbose

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records based on logger name and verbose mode.
        
        Args:
            record: The log record to filter
            
        Returns:
            True if the record should be logged, False otherwise
        """
        if self.verbose:
            return True
        return record.name.startswith('deployment')


def _patch_backend_loggers(verbose: bool = False) -> None:
    """
    Patch backend loggers to use our deployment filter.
    
    Since backend loggers use propagate=False, we need to directly
    modify their handlers to apply our filter.
    """
    # Get the backend command logger
    command_logger = logging.getLogger('backend.src.utils.command')

    # Apply our filter to all existing handlers
    for handler in command_logger.handlers:
        handler.addFilter(DeploymentLogFilter(verbose=verbose))

    # Also patch any future handlers by monkey-patching the addHandler method
    original_add_handler = command_logger.addHandler

    def patched_add_handler(handler):
        handler.addFilter(DeploymentLogFilter(verbose=verbose))
        return original_add_handler(handler)

    command_logger.addHandler = patched_add_handler


def configure_global_logging(verbose: bool = False) -> None:
    """
    Configure global logging with deployment log filtering.
    
    Args:
        verbose: Enable verbose logging (shows all logs including AsyncCommand)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove all existing handlers from root logger
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Add deployment log filter
    handler.addFilter(DeploymentLogFilter(verbose=verbose))

    # Create formatter with filename and line number (matching backend format)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to root logger (this will affect all loggers)
    root_logger.addHandler(handler)

    # Patch backend loggers that don't propagate to root
    _patch_backend_loggers(verbose=verbose)


def setup_logger(name: str, level: Optional[int] = None, verbose: bool = False) -> logging.Logger:
    """
    Setup a logger with consistent formatting and deployment log filtering.

    Args:
        name: Logger name
        level: Logging level (defaults to INFO)
        verbose: Enable verbose logging (shows all logs including AsyncCommand)

    Returns:
        Configured logger instance
    """
    if level is None:
        level = logging.INFO

    # Configure global logging first
    configure_global_logging(verbose=verbose)

    # Create and return the specific logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


__all__ = [
    'setup_logger',
    'configure_global_logging',
    'DeploymentLogFilter'
]
