"""
Requirements file management utility.

This utility handles finding and managing requirements.txt files for deployment.
"""

import os
from pathlib import Path
from typing import Optional, List
from .types import PackageInfo, RequirementsInfo, RequirementsValidationResult


def find_requirements_file(backend_dir: Optional[str] = None) -> Optional[Path]:
    """
    Find the requirements.txt file for the backend.

    Args:
        backend_dir: Path to the backend directory (defaults to 'backend' in current directory)

    Returns:
        Optional[Path]: Path to the requirements.txt file, or None if not found
    """
    if backend_dir is None:
        backend_dir = Path.cwd() / "backend"
    else:
        backend_dir = Path(backend_dir)

    # Check if backend directory exists
    if not backend_dir.exists() or not backend_dir.is_dir():
        return None

    # Look for requirements.txt in the backend directory
    requirements_file = backend_dir / "requirements.txt"

    if requirements_file.exists() and requirements_file.is_file():
        return requirements_file

    return None


def get_requirements_info(requirements_file: Path) -> RequirementsInfo:
    """
    Get information about a requirements.txt file.

    Args:
        requirements_file: Path to the requirements.txt file

    Returns:
        RequirementsInfo: Information about the requirements file
    """
    try:
        # Check if file exists and is readable
        if not requirements_file.exists():
            return RequirementsInfo(
                path=str(requirements_file),
                exists=False,
                readable=False,
                package_count=0,
                packages=[]
            )

        if not requirements_file.is_file():
            return RequirementsInfo(
                path=str(requirements_file),
                exists=True,
                readable=False,
                package_count=0,
                packages=[]
            )

        # Read the file and parse packages
        packages = []
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Parse package specification
                    package_info = _parse_package_line(line, line_num)
                    if package_info:
                        packages.append(package_info)

        except (IOError, UnicodeDecodeError) as e:
            return RequirementsInfo(
                path=str(requirements_file),
                exists=True,
                readable=False,
                package_count=0,
                packages=[],
                error=str(e)
            )

        return RequirementsInfo(
            path=str(requirements_file),
            exists=True,
            readable=True,
            package_count=len(packages),
            packages=packages
        )

    except Exception as e:
        return RequirementsInfo(
            path=str(requirements_file),
            exists=False,
            readable=False,
            package_count=0,
            packages=[],
            error=str(e)
        )


def _parse_package_line(line: str, line_num: int) -> Optional[PackageInfo]:
    """
    Parse a single line from requirements.txt.

    Args:
        line: The line to parse
        line_num: Line number for error reporting

    Returns:
        Optional[PackageInfo]: Package information or None if invalid
    """
    try:
        # Remove any inline comments
        if '#' in line:
            line = line[:line.index('#')].strip()

        if not line:
            return None

        # Handle different requirement formats
        if line.startswith('-r ') or line.startswith('--requirement '):
            # Reference to another requirements file
            ref_file = line.split(' ', 1)[1].strip()
            return PackageInfo(
                type="reference",
                name=ref_file,
                line_number=line_num,
                original_line=line
            )

        elif line.startswith('-e ') or line.startswith('--editable '):
            # Editable install
            package = line.split(' ', 1)[1].strip()
            return PackageInfo(
                type="editable",
                name=package,
                line_number=line_num,
                original_line=line
            )

        elif line.startswith('-f ') or line.startswith('--find-links '):
            # Find links
            url = line.split(' ', 1)[1].strip()
            return PackageInfo(
                type="find_links",
                name=url,
                line_number=line_num,
                original_line=line
            )

        elif line.startswith('-i ') or line.startswith('--index-url '):
            # Index URL
            url = line.split(' ', 1)[1].strip()
            return PackageInfo(
                type="index_url",
                name=url,
                line_number=line_num,
                original_line=line
            )

        else:
            # Regular package specification
            # Parse package name and version constraints
            parts = line.split('==', 1)
            if len(parts) == 2:
                name, version = parts
                return PackageInfo(
                    type="package",
                    name=name.strip(),
                    version=version.strip(),
                    constraint="==",
                    line_number=line_num,
                    original_line=line
                )

            parts = line.split('>=', 1)
            if len(parts) == 2:
                name, version = parts
                return PackageInfo(
                    type="package",
                    name=name.strip(),
                    version=version.strip(),
                    constraint=">=",
                    line_number=line_num,
                    original_line=line
                )

            parts = line.split('<=', 1)
            if len(parts) == 2:
                name, version = parts
                return PackageInfo(
                    type="package",
                    name=name.strip(),
                    version=version.strip(),
                    constraint="<=",
                    line_number=line_num,
                    original_line=line
                )

            parts = line.split('>', 1)
            if len(parts) == 2:
                name, version = parts
                return PackageInfo(
                    type="package",
                    name=name.strip(),
                    version=version.strip(),
                    constraint=">",
                    line_number=line_num,
                    original_line=line
                )

            parts = line.split('<', 1)
            if len(parts) == 2:
                name, version = parts
                return PackageInfo(
                    type="package",
                    name=name.strip(),
                    version=version.strip(),
                    constraint="<",
                    line_number=line_num,
                    original_line=line
                )

            # No version constraint, just package name
            return PackageInfo(
                type="package",
                name=line.strip(),
                version=None,
                constraint=None,
                line_number=line_num,
                original_line=line
            )

    except Exception:
        # If parsing fails, return basic info
        return PackageInfo(
            type="unknown",
            name=line,
            line_number=line_num,
            original_line=line
        )


def validate_requirements_file(requirements_file: Path) -> RequirementsValidationResult:
    """
    Validate a requirements.txt file.

    Args:
        requirements_file: Path to the requirements.txt file

    Returns:
        RequirementsValidationResult: Validation results
    """
    info = get_requirements_info(requirements_file)

    if not info.exists:
        return RequirementsValidationResult(
            valid=False,
            error="Requirements file does not exist",
            info=info
        )

    if not info.readable:
        return RequirementsValidationResult(
            valid=False,
            error="Requirements file is not readable",
            info=info
        )

    if info.package_count == 0:
        return RequirementsValidationResult(
            valid=False,
            error="No packages found in requirements file",
            info=info
        )

    # Check for any parsing errors
    errors = []
    for package in info.packages:
        if package.type == "unknown":
            errors.append(
                f"Line {package.line_number}: Could not parse '{package.original_line}'")

    if errors:
        return RequirementsValidationResult(
            valid=False,
            error="Parsing errors found",
            errors=errors,
            info=info
        )

    return RequirementsValidationResult(
        valid=True,
        info=info
    )


__all__ = [
    "find_requirements_file",
    "get_requirements_info",
    "validate_requirements_file"
]
