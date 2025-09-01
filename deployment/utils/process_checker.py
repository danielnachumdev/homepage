"""
Process checking utilities for deployment.

This module provides utilities to detect and manage running processes,
particularly for checking if frontend/backend services are already running.
"""

import os
import psutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Information about a running process."""
    pid: int
    name: str
    cmdline: List[str]
    cwd: Optional[str]
    status: str
    create_time: float


@dataclass
class ProcessSearchResult:
    """Result of searching for processes."""
    found: bool
    processes: List[ProcessInfo]
    total_count: int
    error: Optional[str] = None


def is_process_running(process_name: str, command_line_pattern: Optional[str] = None,
                       working_directory: Optional[str] = None) -> ProcessSearchResult:
    """
    Check if a process is running with the given criteria.

    Args:
        process_name: Name of the process to search for (e.g., "node.exe", "python.exe")
        command_line_pattern: Optional pattern to match in command line arguments
        working_directory: Optional working directory to match

    Returns:
        ProcessSearchResult containing information about found processes
    """
    try:
        found_processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'status', 'create_time']):
            try:
                proc_info = proc.info

                # Check process name
                if proc_info['name'] and process_name.lower() in proc_info['name'].lower():
                    # Check command line pattern if provided
                    if command_line_pattern:
                        cmdline = ' '.join(
                            proc_info['cmdline']) if proc_info['cmdline'] else ''
                        if command_line_pattern.lower() not in cmdline.lower():
                            continue

                    # Check working directory if provided
                    if working_directory:
                        proc_cwd = proc_info['cwd']
                        if not proc_cwd or not proc_cwd.startswith(working_directory):
                            continue

                    # Create ProcessInfo object
                    process_info = ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'],
                        cmdline=proc_info['cmdline'] or [],
                        cwd=proc_info['cwd'],
                        status=proc_info['status'],
                        create_time=proc_info['create_time']
                    )
                    found_processes.append(process_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                continue

        return ProcessSearchResult(
            found=len(found_processes) > 0,
            processes=found_processes,
            total_count=len(found_processes)
        )

    except Exception as e:
        return ProcessSearchResult(
            found=False,
            processes=[],
            total_count=0,
            error=str(e)
        )


def find_processes_by_name(process_name: str) -> ProcessSearchResult:
    """
    Find all processes with the given name.

    Args:
        process_name: Name of the process to search for

    Returns:
        ProcessSearchResult containing all matching processes
    """
    return is_process_running(process_name)


def find_processes_by_command_line(pattern: str) -> ProcessSearchResult:
    """
    Find processes by command line pattern.

    Args:
        pattern: Pattern to search for in command line arguments

    Returns:
        ProcessSearchResult containing matching processes
    """
    try:
        found_processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'status', 'create_time']):
            try:
                proc_info = proc.info
                cmdline = ' '.join(
                    proc_info['cmdline']) if proc_info['cmdline'] else ''

                if pattern.lower() in cmdline.lower():
                    process_info = ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'],
                        cmdline=proc_info['cmdline'] or [],
                        cwd=proc_info['cwd'],
                        status=proc_info['status'],
                        create_time=proc_info['create_time']
                    )
                    found_processes.append(process_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return ProcessSearchResult(
            found=len(found_processes) > 0,
            processes=found_processes,
            total_count=len(found_processes)
        )

    except Exception as e:
        return ProcessSearchResult(
            found=False,
            processes=[],
            total_count=0,
            error=str(e)
        )


def get_process_info(pid: int) -> Optional[ProcessInfo]:
    """
    Get detailed information about a process by PID.

    Args:
        pid: Process ID

    Returns:
        ProcessInfo if process exists and is accessible, None otherwise
    """
    try:
        proc = psutil.Process(pid)
        proc_info = proc.as_dict(
            ['pid', 'name', 'cmdline', 'cwd', 'status', 'create_time'])

        return ProcessInfo(
            pid=proc_info['pid'],
            name=proc_info['name'],
            cmdline=proc_info['cmdline'] or [],
            cwd=proc_info['cwd'],
            status=proc_info['status'],
            create_time=proc_info['create_time']
        )

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def is_frontend_running(project_root: str, frontend_dir: Optional[str] = None) -> ProcessSearchResult:
    """
    Check if the frontend development server is running.

    Args:
        project_root: Path to the project root directory
        frontend_dir: Path to the frontend directory (defaults to 'frontend' in project root)

    Returns:
        ProcessSearchResult indicating if frontend is running
    """
    if frontend_dir is None:
        frontend_dir = str(Path(project_root) / "frontend")

    # Look for npm processes running 'npm run dev' in the frontend directory
    return is_process_running(
        process_name="node.exe",
        command_line_pattern="npm run dev",
        working_directory=frontend_dir
    )


def is_backend_running(project_root: str, backend_dir: Optional[str] = None) -> ProcessSearchResult:
    """
    Check if the backend server is running.

    Args:
        project_root: Path to the project root directory
        backend_dir: Path to the backend directory (defaults to 'backend' in project root)

    Returns:
        ProcessSearchResult indicating if backend is running
    """
    if backend_dir is None:
        backend_dir = str(Path(project_root) / "backend")

    # Look for Python processes running __main__.py in the backend directory
    return is_process_running(
        process_name="python.exe",
        command_line_pattern="__main__.py",
        working_directory=backend_dir
    )


def kill_process(pid: int, timeout: int = 10) -> bool:
    """
    Kill a process by PID with graceful termination.

    Args:
        pid: Process ID to kill
        timeout: Timeout in seconds for graceful termination

    Returns:
        True if process was killed successfully, False otherwise
    """
    try:
        proc = psutil.Process(pid)

        # Try graceful termination first
        proc.terminate()

        try:
            proc.wait(timeout=timeout)
            return True
        except psutil.TimeoutExpired:
            # Force kill if graceful termination failed
            proc.kill()
            proc.wait()
            return True

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
    except Exception:
        return False


def get_system_info() -> Dict[str, Any]:
    """
    Get system information relevant to process management.

    Returns:
        Dictionary containing system information
    """
    try:
        return {
            "platform": os.name,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "boot_time": psutil.boot_time(),
            "process_count": len(psutil.pids())
        }
    except Exception as e:
        return {
            "platform": os.name,
            "error": str(e)
        }


__all__ = [
    "ProcessInfo",
    "ProcessSearchResult",
    "is_process_running",
    "find_processes_by_name",
    "find_processes_by_command_line",
    "get_process_info",
    "is_frontend_running",
    "is_backend_running",
    "kill_process",
    "get_system_info"
]
