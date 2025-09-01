"""
Command execution utilities.

This module provides the CommandExecutor class for executing arbitrary commands
with basic process management.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Union, List, TextIO
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of executing a command."""

    success: bool
    process: Optional[subprocess.Popen]
    pid: Optional[int]
    stdout_log: Optional[Path]
    stderr_log: Optional[Path]
    error_message: Optional[str]

    @property
    def is_running(self) -> bool:
        """Check if the process is currently running."""
        if self.process is None:
            return False
        return self.process.poll() is None


class CommandExecutor:
    """Static class for executing arbitrary commands."""

    @staticmethod
    def execute(
        command: Union[str, List[str]],
        shell: bool = False,
        detached: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        log_dir: Optional[Union[str, Path]] = None,
        log_prefix: str = "process"
    ) -> CommandResult:
        """
        Execute a command with basic process management.

        Args:
            command: Command to execute (string or list of strings)
            shell: Whether to use shell execution (default: False)
            detached: Whether to detach the process from parent (default: False)
            cwd: Working directory for the process
            log_dir: Directory for log files (if None, no logging)
            log_prefix: Prefix for log file names (default: "process")

        Returns:
            CommandResult: Type-safe result containing command execution information
        """
        try:
            # Set up logging if requested
            stdout_file = None
            stderr_file = None
            stdout_log = None
            stderr_log = None

            if log_dir is not None:
                log_dir = Path(log_dir)
                log_dir.mkdir(exist_ok=True)

                stdout_log = log_dir / f"{log_prefix}_stdout.log"
                stderr_log = log_dir / f"{log_prefix}_stderr.log"

                stdout_file = open(stdout_log, 'w', encoding='utf-8')
                stderr_file = open(stderr_log, 'w', encoding='utf-8')

            # Create the process
            process = CommandExecutor._create_process_internal(
                command=command,
                detached=detached,
                cwd=cwd,
                stdout=stdout_file,
                stderr=stderr_file,
                shell=shell
            )

            # Close file handles if we opened them
            if stdout_file:
                stdout_file.close()
            if stderr_file:
                stderr_file.close()

            return CommandResult(
                success=True,
                process=process,
                pid=process.pid,
                stdout_log=stdout_log,
                stderr_log=stderr_log,
                error_message=None
            )

        except Exception as e:
            # Clean up file handles on error
            if stdout_file:
                stdout_file.close()
            if stderr_file:
                stderr_file.close()

            return CommandResult(
                success=False,
                process=None,
                pid=None,
                stdout_log=stdout_log,
                stderr_log=stderr_log,
                error_message=str(e)
            )

    @staticmethod
    def _create_process_internal(
        command: Union[str, List[str]],
        detached: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        stdout: Optional[Union[TextIO, int]] = None,
        stderr: Optional[Union[TextIO, int]] = None,
        shell: bool = False
    ) -> subprocess.Popen:
        """Internal function to create a process with platform-specific detachment."""
        # Set default outputs if not provided
        if stdout is None:
            stdout = subprocess.DEVNULL
        if stderr is None:
            stderr = subprocess.DEVNULL

        if detached:
            if sys.platform == 'win32':
                # Windows: use creation flags to detach
                DETACHED_PROCESS = 0x00000008
                return subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=stdout,
                    stderr=stderr,
                    text=True,
                    shell=shell,
                    creationflags=DETACHED_PROCESS,
                    close_fds=True
                )
            else:
                # Unix/Linux/macOS: use preexec_fn to detach
                import os
                return subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=stdout,
                    stderr=stderr,
                    text=True,
                    shell=shell,
                    preexec_fn=os.setpgrp,
                    close_fds=True
                )
        else:
            return subprocess.Popen(
                command,
                cwd=cwd,
                stdout=stdout,
                stderr=stderr,
                text=True,
                shell=shell
            )


__all__ = [
    "CommandExecutor",
    "CommandResult"
]
