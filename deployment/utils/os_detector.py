"""
Operating System Detection Utility
Detects the OS and returns the OS type.
"""

import os
import platform


def detect_os() -> str:
    """
    Detect the operating system and return the OS type.

    Returns:
        str: OS type ('windows', 'linux', 'macos', or 'unknown')
    """
    os_name = os.name
    platform_system = platform.system().lower()

    # Determine the primary OS
    if os_name == 'nt' or platform_system == 'windows':
        return 'windows'
    elif platform_system == 'linux':
        return 'linux'
    elif platform_system == 'darwin':
        return 'macos'
    else:
        return 'unknown'


__all__ = [
    'detect_os'
]
