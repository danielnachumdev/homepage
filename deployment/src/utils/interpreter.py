"""
Python interpreter detection utility.

This utility finds the correct Python interpreter to use for deployment,
prioritizing virtual environments over system Python.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from .types import InterpreterInfo
from backend.src.utils.command import AsyncCommand


async def find_python_interpreter(project_root: Optional[str] = None,
                            backend_dir: Optional[str] = None) -> str:
    """
    Find the best Python interpreter to use for deployment.

    Priority order:
    1. Virtual environment in project_root/venv/ (Windows: Scripts/python.exe, Linux: bin/python)
    2. Virtual environment in backend_dir/venv/ (Windows: Scripts/python.exe, Linux: bin/python)
    3. Current sys.executable (fallback)

    Args:
        project_root: Path to the project root directory (defaults to current working directory)
        backend_dir: Path to the backend directory (defaults to 'backend' in project root)

    Returns:
        str: Path to the Python interpreter to use
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    if backend_dir is None:
        backend_dir = project_root / "backend"
    else:
        backend_dir = Path(backend_dir)

    # List of potential interpreter paths to check
    interpreter_candidates = []

    # 1. Check for virtual environment in project root
    project_venv_paths = [
        project_root / "venv" / "Scripts" / "python.exe",  # Windows
        project_root / "venv" / "bin" / "python",          # Linux/macOS
        project_root / "venv" / "Scripts" /
        "python",      # Windows (alternative)
    ]
    interpreter_candidates.extend(project_venv_paths)

    # 2. Check for virtual environment in backend directory
    backend_venv_paths = [
        backend_dir / "venv" / "Scripts" / "python.exe",   # Windows
        backend_dir / "venv" / "bin" / "python",           # Linux/macOS
        backend_dir / "venv" / "Scripts" /
        "python",       # Windows (alternative)
    ]
    interpreter_candidates.extend(backend_venv_paths)

    # 3. Add current sys.executable as fallback
    interpreter_candidates.append(sys.executable)

    # Test each candidate
    for interpreter_path in interpreter_candidates:
        if await _is_valid_python_interpreter(interpreter_path):
            return str(interpreter_path)

    # If we get here, something is very wrong
    raise RuntimeError("No valid Python interpreter found")


async def _is_valid_python_interpreter(interpreter_path: Path) -> bool:
    """
    Check if a Python interpreter is valid and working.

    Args:
        interpreter_path: Path to the Python interpreter to test

    Returns:
        bool: True if the interpreter is valid and working
    """
    try:
        # Check if the file exists
        if not interpreter_path.exists():
            return False

        # Try to run the interpreter
        cmd = AsyncCommand([str(interpreter_path), '--version'])
        result = await cmd.execute()

        # If we get here, the interpreter works
        return result.success

    except Exception:
        return False


async def get_interpreter_info(interpreter_path: str) -> InterpreterInfo:
    """
    Get information about a Python interpreter.

    Args:
        interpreter_path: Path to the Python interpreter

    Returns:
        dict: Information about the interpreter
    """
    try:
        # Get version
        version_cmd = AsyncCommand([interpreter_path, '--version'])
        version_result = await version_cmd.execute()

        # Get executable path
        executable_cmd = AsyncCommand([interpreter_path, '-c', 'import sys; print(sys.executable)'])
        executable_result = await executable_cmd.execute()

        # Check if it's in a virtual environment
        venv_cmd = AsyncCommand([interpreter_path, '-c',
            'import sys; print(hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))'])
        venv_result = await venv_cmd.execute()

        is_venv = venv_result.stdout.strip().lower() == 'true'

        return InterpreterInfo(
            path=interpreter_path,
            version=version_result.stdout.strip(),
            executable=executable_result.stdout.strip(),
            is_virtual_env=is_venv,
            working=version_result.success and executable_result.success and venv_result.success
        )

    except Exception as e:
        return InterpreterInfo(
            path=interpreter_path,
            version="unknown",
            executable=interpreter_path,
            is_virtual_env=False,
            working=False,
            error=str(e)
        )


async def list_available_interpreters(project_root: Optional[str] = None,
                                backend_dir: Optional[str] = None) -> List[InterpreterInfo]:
    """
    List all available Python interpreters in order of preference.

    Args:
        project_root: Path to the project root directory
        backend_dir: Path to the backend directory

    Returns:
        List[InterpreterInfo]: List of interpreter information objects
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    if backend_dir is None:
        backend_dir = project_root / "backend"
    else:
        backend_dir = Path(backend_dir)

    # List of potential interpreter paths to check
    interpreter_candidates = []

    # 1. Check for virtual environment in project root
    project_venv_paths = [
        project_root / "venv" / "Scripts" / "python.exe",  # Windows
        project_root / "venv" / "bin" / "python",          # Linux/macOS
        project_root / "venv" / "Scripts" /
        "python",      # Windows (alternative)
    ]
    interpreter_candidates.extend(project_venv_paths)

    # 2. Check for virtual environment in backend directory
    backend_venv_paths = [
        backend_dir / "venv" / "Scripts" / "python.exe",   # Windows
        backend_dir / "venv" / "bin" / "python",           # Linux/macOS
        backend_dir / "venv" / "Scripts" /
        "python",       # Windows (alternative)
    ]
    interpreter_candidates.extend(backend_venv_paths)

    # 3. Add current sys.executable as fallback
    interpreter_candidates.append(Path(sys.executable))

    # Test each candidate and collect info
    interpreters = []
    for interpreter_path in interpreter_candidates:
        info = await get_interpreter_info(str(interpreter_path))
        if info.working:
            interpreters.append(info)

    return interpreters


__all__ = [
    "find_python_interpreter",
    "get_interpreter_info",
    "list_available_interpreters"
]
