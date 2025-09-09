import logging
import sys
import io
from typing import Optional


class UTF8StreamHandler(logging.StreamHandler):
    """Custom StreamHandler that ensures UTF-8 encoding."""

    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stdout
        super().__init__(stream)
        # Ensure the stream uses UTF-8 encoding
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='replace')
            except (AttributeError, OSError):
                pass

    def emit(self, record):
        try:
            msg = self.format(record)
            # Ensure the message is properly encoded
            if isinstance(msg, str):
                # Write as UTF-8 bytes to handle Unicode properly
                self.stream.write(msg + self.terminator)
            else:
                self.stream.write(str(msg) + self.terminator)
            self.flush()
        except UnicodeError:
            # Fallback for Unicode issues
            try:
                self.stream.write(f"Unicode error in log: {record.getMessage()}\n")
                self.flush()
            except Exception:
                # Last resort - write to stderr
                sys.stderr.write(f"Critical logging error: {record.getMessage()}\n")


class ExtraDataFormatter(logging.Formatter):
    """Custom formatter that includes extra data from log records."""

    def format(self, record: logging.LogRecord) -> str:
        try:
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
                # Handle Unicode characters safely
                sorted_items = sorted(data.items())
                data_pairs = []
                for k, v in sorted_items:
                    try:
                        # Ensure both key and value are properly encoded
                        k_str = str(k) if k is not None else 'None'
                        v_str = str(v) if v is not None else 'None'
                        data_pairs.append(f"{k_str}={v_str}")
                    except UnicodeError:
                        # Fallback for problematic Unicode characters
                        data_pairs.append(f"{repr(k)}={repr(v)}")

                data_str = " | " + " | ".join(data_pairs)
                return base_message + data_str

            return base_message
        except UnicodeError as e:
            # Fallback for any Unicode issues
            return f"Unicode error in log formatting: {e} | {record.getMessage()}"


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

    # Create console handler that outputs to stdout with UTF-8 encoding
    console_handler = UTF8StreamHandler(sys.stdout)
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
    "UTF8StreamHandler",
    "ExtraDataFormatter",
    "setup_logger",
    "get_logger",
    "default_logger"
]
