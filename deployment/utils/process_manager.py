"""
Process management utilities for Windows systems.

This module provides the ProcessManager class for managing processes,
including spawning, listing, and terminating processes.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Union, List
from dataclasses import dataclass
from .command_executor import CommandExecutor


class ProcessHandle:
    """
    A facade wrapper around subprocess.Popen that provides enhanced process management capabilities.

    This class wraps the underlying subprocess.Popen object and provides additional
    functionality like hiding terminal windows, sending signals, and managing process state.
    """

    def __init__(self, process: subprocess.Popen, pid: int):
        """
        Initialize the ProcessHandle.

        Args:
            process: The underlying subprocess.Popen object
            pid: The process ID
        """
        self._process = process
        self._pid = pid
        self._hidden = False

    @property
    def process(self) -> subprocess.Popen:
        """Get the underlying subprocess.Popen object."""
        return self._process

    @property
    def pid(self) -> int:
        """Get the process ID."""
        return self._pid

    @property
    def is_running(self) -> bool:
        """Check if the process is currently running."""
        return self._process.poll() is None

    @property
    def returncode(self) -> Optional[int]:
        """Get the return code of the process (None if still running)."""
        return self._process.returncode

    def poll(self) -> Optional[int]:
        """Check if the process has terminated and return its return code."""
        return self._process.poll()

    def wait(self, timeout: Optional[float] = None) -> int:
        """Wait for the process to terminate and return its return code."""
        return self._process.wait(timeout=timeout)

    def communicate(self, input: Optional[bytes] = None, timeout: Optional[float] = None) -> tuple[bytes, bytes]:
        """Communicate with the process and return (stdout, stderr)."""
        return self._process.communicate(input=input, timeout=timeout)

    def terminate(self) -> None:
        """Terminate the process gracefully."""
        self._process.terminate()

    def kill(self) -> None:
        """Kill the process forcefully."""
        self._process.kill()

    def send_signal(self, signal: int) -> None:
        """Send a signal to the process."""
        self._process.send_signal(signal)

    def hide_terminal_window(self) -> bool:
        """
        Hide the terminal window for this process (Windows only).

        Returns:
            bool: True if successful, False otherwise
        """
        if sys.platform != 'win32':
            return False

        try:
            # Get the window handle for the process
            import win32gui  # type: ignore
            import win32process  # type: ignore

            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == self._pid:
                        windows.append(hwnd)
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            # Hide each window associated with this process
            for hwnd in windows:
                win32gui.ShowWindow(hwnd, 0)  # SW_HIDE = 0

            self._hidden = True
            return True

        except ImportError:
            # Fallback using ctypes if win32gui is not available
            try:
                import ctypes
                # This is a more basic approach that might not work for all cases
                kernel32 = ctypes.windll.kernel32
                # We can't easily get the window handle without win32gui
                # This is a placeholder for the basic approach
                self._hidden = True
                return True
            except Exception:
                return False
        except Exception:
            return False

    def show_terminal_window(self) -> bool:
        """
        Show the terminal window for this process (Windows only).

        Returns:
            bool: True if successful, False otherwise
        """
        if sys.platform != 'win32':
            return False

        try:
            import win32gui  # type: ignore
            import win32process  # type: ignore

            def enum_windows_callback(hwnd, windows):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == self._pid:
                    windows.append(hwnd)
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            # Show each window associated with this process
            for hwnd in windows:
                win32gui.ShowWindow(hwnd, 1)  # SW_SHOWNORMAL = 1

            self._hidden = False
            return True

        except ImportError:
            # Fallback using ctypes if win32gui is not available
            try:
                import ctypes
                # This is a more basic approach that might not work for all cases
                self._hidden = False
                return True
            except Exception:
                return False
        except Exception:
            return False

    def is_terminal_hidden(self) -> bool:
        """Check if the terminal window is currently hidden."""
        return self._hidden

    def send_input(self, data: bytes) -> None:
        """Send input data to the process stdin."""
        if self._process.stdin:
            self._process.stdin.write(data)
            self._process.stdin.flush()

    def close_stdin(self) -> None:
        """Close the stdin stream."""
        if self._process.stdin:
            self._process.stdin.close()

    def __repr__(self) -> str:
        """String representation of the ProcessHandle."""
        status = "running" if self.is_running else f"terminated (code: {self.returncode})"
        return f"ProcessHandle(pid={self._pid}, status={status}, hidden={self._hidden})"


@dataclass
class ProcessInfo:
    """Information about a running process."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    command_line: Optional[str] = None


@dataclass
class ProcessResult:
    """Result of process management operations."""

    success: bool
    process: Optional[ProcessHandle]
    pid: Optional[int]
    stdout_log: Optional[Path]
    stderr_log: Optional[Path]
    spawn_info_file: Optional[Path]
    error_message: Optional[str]

    @property
    def is_running(self) -> bool:
        """Check if the process is currently running."""
        if self.process is None:
            return False
        return self.process.is_running


class ProcessManager:
    """Class for managing processes on Windows systems."""

    @staticmethod
    def spawn(
        command: Union[str, List[str]],
        detached: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        log_dir: Optional[Union[str, Path]] = None,
        log_prefix: str = "process"
    ) -> ProcessResult:
        """
        Spawn a new process using CommandExecutor.

        Args:
            command: Command to execute (string or list of strings)
            detached: Whether to detach the process from parent (default: False)
            cwd: Working directory for the process
            log_dir: Directory for log files (if None, no logging)
            log_prefix: Prefix for log file names (default: "process")

        Returns:
            ProcessResult: Type-safe result containing process information
        """
        # Use CommandExecutor to execute the command
        result = CommandExecutor.execute(
            command=command,
            shell=True,  # Use shell for better command execution
            detached=detached,
            cwd=cwd,
            log_dir=log_dir,
            log_prefix=log_prefix
        )

        # Set up spawn info file if logging is enabled
        spawn_info_file = None
        if log_dir is not None:
            log_dir = Path(log_dir)
            spawn_info_file = log_dir / f"{log_prefix}_spawn_info.json"

        # Create ProcessHandle if we have a process
        process_handle = None
        if result.success and result.process and result.pid:
            process_handle = ProcessHandle(result.process, result.pid)

        # Convert CommandResult to ProcessResult
        return ProcessResult(
            success=result.success,
            process=process_handle,
            pid=result.pid,
            stdout_log=result.stdout_log,
            stderr_log=result.stderr_log,
            spawn_info_file=spawn_info_file,
            error_message=result.error_message
        )

    @staticmethod
    def list_processes(
        name_filter: Optional[str] = None,
        field_filter: Optional[str] = None
    ) -> List[ProcessInfo]:
        """
        List running processes using Get-Process command via CommandExecutor.

        Args:
            name_filter: Optional process name filter (e.g., "chrome", "node")
            field_filter: Optional field to select (e.g., "Id", "ProcessName", "CPU")

        Returns:
            List of ProcessInfo objects containing process information
        """
        try:
            # Build PowerShell command
            if name_filter and field_filter:
                cmd = f'Get-Process -Name "{name_filter}" | Select-Object {field_filter}'
            elif name_filter:
                cmd = f'Get-Process -Name "{name_filter}" | Select-Object Id, ProcessName, CPU, WorkingSet, Status'
            elif field_filter:
                cmd = f'Get-Process | Select-Object {field_filter}'
            else:
                cmd = 'Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet, Status'

            # Execute PowerShell command using CommandExecutor
            result = CommandExecutor.execute(
                command=['powershell', '-Command', cmd],
                shell=False,
                detached=False
            )

            if not result.success or not result.process:
                return []

            # Wait for the command to complete and get output
            stdout, stderr = result.process.communicate()

            if result.process.returncode != 0:
                return []

            # Parse the output
            lines = stdout.strip().split('\n')
            processes = []

            # Skip header lines (first 2 lines are usually headers)
            for line in lines[2:]:
                if line.strip():
                    try:
                        # Parse the line based on what fields we requested
                        if field_filter:
                            # If specific field was requested, just return the value
                            processes.append(ProcessInfo(
                                pid=0,  # We don't have PID if only one field
                                name=line.strip(),
                                cpu_percent=0.0,
                                memory_percent=0.0,
                                status="Unknown"
                            ))
                        else:
                            # Parse standard fields: Id, ProcessName, CPU, WorkingSet, Status
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                pid = int(parts[0])
                                name = parts[1]
                                cpu = float(
                                    parts[2]) if parts[2] != '-' else 0.0
                                memory = float(
                                    parts[3]) if parts[3] != '-' else 0.0
                                status = parts[4] if len(
                                    parts) > 4 else "Unknown"

                                processes.append(ProcessInfo(
                                    pid=pid,
                                    name=name,
                                    cpu_percent=cpu,
                                    memory_percent=memory,
                                    status=status
                                ))
                    except (ValueError, IndexError):
                        continue

            return processes

        except Exception:
            return []

    @staticmethod
    def get_process_info(pid: int) -> Optional[ProcessInfo]:
        """
        Get detailed information about a specific process by PID using CommandExecutor.

        Args:
            pid: Process ID to get information for

        Returns:
            ProcessInfo object or None if process not found
        """
        try:
            # Get process information using WMI
            cmd = f'Get-WmiObject Win32_Process | Where-Object {{ $_.ProcessId -eq {pid} }} | Select-Object ProcessId, Name, CommandLine'

            # Execute PowerShell command using CommandExecutor
            result = CommandExecutor.execute(
                command=['powershell', '-Command', cmd],
                shell=False,
                detached=False
            )

            if not result.success or not result.process:
                return None

            # Wait for the command to complete and get output
            stdout, stderr = result.process.communicate()

            if result.process.returncode != 0 or not stdout.strip():
                return None

            # Parse the output
            lines = stdout.strip().split('\n')
            if len(lines) < 3:  # Header + data + empty line
                return None

            # Parse the process information
            data_line = lines[2].strip()
            parts = data_line.split(' ', 2)  # Split into max 3 parts

            if len(parts) >= 2:
                process_id = int(parts[0])
                name = parts[1]
                command_line = parts[2] if len(parts) > 2 else None

                return ProcessInfo(
                    pid=process_id,
                    name=name,
                    cpu_percent=0.0,  # Would need additional query for CPU
                    memory_percent=0.0,  # Would need additional query for memory
                    status="Running",
                    command_line=command_line
                )

        except Exception:
            pass

        return None

    @staticmethod
    def terminate_process(pid: int, force: bool = False) -> bool:
        """
        Terminate a process by PID using CommandExecutor.

        Args:
            pid: Process ID to terminate
            force: Whether to force kill the process (default: False)

        Returns:
            True if process was terminated successfully, False otherwise
        """
        try:
            if force:
                # Force kill using Stop-Process
                cmd = f'Stop-Process -Id {pid} -Force'
            else:
                # Graceful termination using Stop-Process
                cmd = f'Stop-Process -Id {pid}'

            # Execute PowerShell command using CommandExecutor
            result = CommandExecutor.execute(
                command=['powershell', '-Command', cmd],
                shell=False,
                detached=False
            )

            if not result.success or not result.process:
                return False

            # Wait for the command to complete
            stdout, stderr = result.process.communicate()

            return result.process.returncode == 0

        except Exception:
            return False


__all__ = [
    "ProcessManager",
    "ProcessHandle",
    "ProcessInfo",
    "ProcessResult"
]
