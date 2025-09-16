"""
Type definitions for deployment utilities.

This module contains dataclasses and type definitions for type-safe
return values from deployment utilities.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from pathlib import Path


@dataclass
class InterpreterInfo:
    """Information about a Python interpreter."""
    path: str
    version: str
    executable: str
    is_virtual_env: bool
    working: bool
    error: Optional[str] = None


@dataclass
class PackageInfo:
    """Information about a package from requirements.txt."""
    type: str  # 'package', 'reference', 'editable', 'find_links', 'index_url', 'unknown'
    name: str
    line_number: int
    original_line: str
    version: Optional[str] = None
    constraint: Optional[str] = None  # '==', '>=', '<=', '>', '<'


@dataclass
class RequirementsInfo:
    """Information about a requirements.txt file."""
    path: str
    exists: bool
    readable: bool
    package_count: int
    packages: List[PackageInfo]
    error: Optional[str] = None


@dataclass
class RequirementsValidationResult:
    """Result of validating a requirements.txt file."""
    valid: bool
    error: Optional[str] = None
    errors: Optional[List[str]] = None
    info: Optional[RequirementsInfo] = None


__all__ = [
    "InterpreterInfo",
    "PackageInfo",
    "RequirementsInfo",
    "RequirementsValidationResult"
]
