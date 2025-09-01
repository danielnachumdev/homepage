# Utils package for deployment CLI

from .logger import *
from .os_detector import *

__all__ = [
    "setup_logger",
    "detect_os"
]
