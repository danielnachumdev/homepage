"""
Process checking utilities for detecting running processes.
"""

import sys
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from backend.src.utils.command import AsyncCommand


@dataclass
class ProcessSearchResult:
    """Result of searching for processes."""

    found: bool
    processes: List[dict]
    total_count: int


async def is_frontend_running(project_root: str, frontend_dir: Optional[str] = None) -> ProcessSearchResult:
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
        return await _is_frontend_running_windows(project_root, frontend_dir)
    else:
        return await _is_frontend_running_unix(project_root, frontend_dir)


async def _is_frontend_running_windows(project_root: str, frontend_dir: str) -> ProcessSearchResult:
    """Windows-specific frontend process detection."""
    try:
        # Get all cmd.exe processes
        cmd = AsyncCommand.powershell("Get-Process cmd | Select-Object Id")
        result = await cmd.execute()

        if not result.success:
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
                cmd = AsyncCommand.powershell(
                    f'Get-WmiObject Win32_Process | Where-Object {{ $_.ProcessId -eq {pid} }} | Select-Object -ExpandProperty CommandLine'
                )
                cmd_result = await cmd.execute()

                if cmd_result.success and cmd_result.stdout.strip():
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

            except Exception:
                continue

        return ProcessSearchResult(
            found=len(found_processes) > 0,
            processes=found_processes,
            total_count=len(found_processes)
        )

    except Exception:
        return ProcessSearchResult(found=False, processes=[], total_count=0)


async def _is_frontend_running_unix(project_root: str, frontend_dir: str) -> ProcessSearchResult:
    """Unix/Linux/macOS-specific frontend process detection."""
    # Simple implementation for Unix systems
    try:
        cmd = AsyncCommand.cmd("ps aux")
        result = await cmd.execute()

        if not result.success:
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


async def is_backend_running(project_root: str, backend_dir: Optional[str] = None) -> ProcessSearchResult:
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
            cmd = AsyncCommand.powershell("Get-Process python | Select-Object Id")
        else:
            cmd = AsyncCommand.cmd("ps aux")
        
        result = await cmd.execute()

        if not result.success:
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


async def kill_process(pid: int, timeout: int = 10) -> bool:
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
            # Use PowerShell to terminate the process gracefully first
            cmd = AsyncCommand.powershell(f'Stop-Process -Id {pid} -Force')
        else:
            # Use kill command on Unix systems
            cmd = AsyncCommand.cmd(f'kill -TERM {pid}')

        result = await cmd.execute()
        return result.success

    except Exception:
        return False


async def kill_processes_carefully(processes: List[dict], project_root: str, 
                                 backend_dir: str, frontend_dir: str, logger) -> bool:
    """
    Carefully kill processes, ensuring we only kill our specific processes.

    Args:
        processes: List of process dictionaries to kill
        project_root: Project root directory for validation
        backend_dir: Backend directory for validation
        frontend_dir: Frontend directory for validation

    Returns:
        True if all processes were killed successfully, False otherwise
    """
    success_count = 0
    total_count = len(processes)

    for proc in processes:
        try:
            pid = proc['pid']
            cmdline = proc.get('cmdline', '')
            cwd = proc.get('cwd', '')

            # Additional validation to ensure we're killing the right process
            is_our_process = False

            # Check if it's a backend process
            if ('python' in cmdline.lower() and 
                '__main__.py' in cmdline and 
                backend_dir in cwd):
                is_our_process = True
                logger.info(f"Identified backend process: PID {pid}")

            # Check if it's a frontend process
            elif ('npm' in cmdline.lower() and 
                  'run' in cmdline and 
                  'dev' in cmdline and 
                  frontend_dir in cwd):
                is_our_process = True
                logger.info(f"Identified frontend process: PID {pid}")

            # Check if it's a cmd.exe process running our dev server
            elif ('cmd.exe' in cmdline and 
                  any(server in cmdline.lower() for server in ['vite', 'webpack', 'next', 'react-scripts', 'serve', 'dev']) and
                  frontend_dir in cwd):
                is_our_process = True
                logger.info(f"Identified frontend cmd process: PID {pid}")

            if is_our_process:
                if await kill_process(pid):
                    success_count += 1
                    logger.info(f"Successfully killed process PID {pid}")
                else:
                    logger.warning(f"Failed to kill process PID {pid}")
            else:
                logger.warning(f"Skipping process PID {pid} - not identified as our process")
                logger.warning(f"Command line: {cmdline}")
                logger.warning(f"Working directory: {cwd}")

        except Exception as e:
            logger.error(f"Error killing process {proc}: {e}")

    return success_count == total_count


__all__ = [
    "is_frontend_running",
    "is_backend_running",
    "kill_process",
    "kill_processes_carefully",
    "ProcessSearchResult"
]
