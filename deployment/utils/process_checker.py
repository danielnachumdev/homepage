"""
Process checking utilities for detecting running processes.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ProcessSearchResult:
    """Result of searching for processes."""

    found: bool
    processes: List[dict]
    total_count: int


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

    # On Windows, npm run dev typically spawns a cmd.exe process
    if sys.platform == 'win32':
        return _is_frontend_running_windows(project_root, frontend_dir)
    else:
        return _is_frontend_running_unix(project_root, frontend_dir)


def _is_frontend_running_windows(project_root: str, frontend_dir: str) -> ProcessSearchResult:
    """Windows-specific frontend process detection."""
    try:
        # Get all cmd.exe processes
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Process cmd | Select-Object Id'],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode != 0:
            return ProcessSearchResult(found=False, processes=[], total_count=0)

        # Parse the output to get PIDs
        lines = result.stdout.strip().split('\n')
        cmd_pids = []

        for line in lines[2:]:  # Skip header lines
            if line.strip():
                try:
                    pid = int(line.strip())
                    cmd_pids.append(pid)
                except ValueError:
                    continue

        # Check each cmd.exe process for our dev server command
        found_processes = []

        for pid in cmd_pids:
            try:
                # Get command line for this process
                cmd_result = subprocess.run(
                    ['powershell', '-Command',
                     f'Get-WmiObject Win32_Process | Where-Object {{ $_.ProcessId -eq {pid} }} | Select-Object -ExpandProperty CommandLine'],
                    capture_output=True,
                    text=True,
                    shell=True
                )

                if cmd_result.returncode == 0 and cmd_result.stdout.strip():
                    command_line = cmd_result.stdout.strip()

                    # Check if this is our dev server process
                    if ('cmd.exe /d /s /c' in command_line and
                            any(server in command_line.lower() for server in ['vite', 'webpack', 'next', 'react-scripts', 'serve', 'dev'])):

                        found_processes.append({
                            'pid': pid,
                            'name': 'cmd.exe',
                            'cmdline': command_line,
                            'cwd': frontend_dir,
                            'status': 'running'
                        })

            except (subprocess.CalledProcessError, ValueError):
                continue

        return ProcessSearchResult(
            found=len(found_processes) > 0,
            processes=found_processes,
            total_count=len(found_processes)
        )

    except Exception:
        return ProcessSearchResult(found=False, processes=[], total_count=0)


def _is_frontend_running_unix(project_root: str, frontend_dir: str) -> ProcessSearchResult:
    """Unix/Linux/macOS-specific frontend process detection."""
    # Simple implementation for Unix systems
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return ProcessSearchResult(found=False, processes=[], total_count=0)

        # Look for npm or node processes
        lines = result.stdout.split('\n')
        found_processes = []

        for line in lines:
            if 'npm' in line and 'run' in line and 'dev' in line:
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pid = int(parts[1])
                        found_processes.append({
                            'pid': pid,
                            'name': 'npm',
                            'cmdline': line,
                            'cwd': frontend_dir,
                            'status': 'running'
                        })
                    except ValueError:
                        continue

        return ProcessSearchResult(
            found=len(found_processes) > 0,
            processes=found_processes,
            total_count=len(found_processes)
        )

    except Exception:
        return ProcessSearchResult(found=False, processes=[], total_count=0)


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
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['powershell', '-Command', 'Get-Process python | Select-Object Id'],
                capture_output=True,
                text=True,
                shell=True
            )
        else:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )

        if result.returncode != 0:
            return ProcessSearchResult(found=False, processes=[], total_count=0)

        # Simple implementation - look for python processes
        found_processes = []
        lines = result.stdout.split('\n')

        for line in lines:
            if 'python' in line.lower() and '__main__.py' in line:
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pid = int(parts[1])
                        found_processes.append({
                            'pid': pid,
                            'name': 'python',
                            'cmdline': line,
                            'cwd': backend_dir,
                            'status': 'running'
                        })
                    except ValueError:
                        continue

        return ProcessSearchResult(
            found=len(found_processes) > 0,
            processes=found_processes,
            total_count=len(found_processes)
        )

    except Exception:
        return ProcessSearchResult(found=False, processes=[], total_count=0)


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
        if sys.platform == 'win32':
            # Use PowerShell to terminate the process
            result = subprocess.run(
                ['powershell', '-Command', f'Stop-Process -Id {pid}'],
                capture_output=True,
                text=True,
                shell=True
            )
        else:
            # Use kill command on Unix systems
            result = subprocess.run(
                ['kill', str(pid)],
                capture_output=True,
                text=True
            )

        return result.returncode == 0

    except Exception:
        return False


__all__ = [
    "is_frontend_running",
    "is_backend_running",
    "kill_process",
    "ProcessSearchResult"
]
