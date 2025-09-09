"""
Generic AsyncCommand class for standardized async command execution.

This module provides a comprehensive AsyncCommand class that encapsulates command execution
with state tracking, result handling, and CLI/GUI strategy support using async patterns.
"""

import asyncio
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union, Callable, Dict
from datetime import datetime

try:
    from ..schemas.v1.system import CommandResult, CommandResponse
    from ..utils.logger import get_logger
except ImportError:
    # Fallback for when running as standalone

    class CommandResult:
        """Comprehensive result object for command execution."""

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class CommandResponse:
        """Response object for command execution."""

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def get_logger(name):
        import logging
        return logging.getLogger(name)


class CommandState(Enum):
    """Enumeration of possible command states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    KILLED = "killed"


class CommandType(Enum):
    """Enumeration of command types."""
    CLI = "cli"
    GUI = "gui"


@dataclass
class CommandExecutionResult:
    """Result of command execution with comprehensive details."""
    command: 'AsyncCommand'
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    state: CommandState
    killed: bool = False
    timeout_occurred: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pid: Optional[int] = None
    command_type: CommandType = CommandType.CLI
    exception: Optional[Exception] = None

    def __str__(self) -> str:
        """String representation of the result."""
        status = "SUCCESS" if self.success else "FAILED"
        if self.timeout_occurred:
            status = "TIMEOUT"
        elif self.killed:
            status = "KILLED"

        return f"CommandExecutionResult(command={self.command}, success={self.success}, return_code={self.return_code}, stdout='{self.stdout}', stderr='{self.stderr}', execution_time={self.execution_time}, state={self.state}, killed={self.killed}, timeout_occurred={self.timeout_occurred}, start_time={self.start_time}, end_time={self.end_time}, pid={self.pid}, command_type={self.command_type}, exception={self.exception}) - {status}"


class AsyncCommand:
    """
    Generic async command execution class with comprehensive state tracking and result handling.

    This class provides a unified interface for executing commands with support for:
    - Async execution with proper event loop management
    - State tracking (pending, running, completed, failed, timeout, killed)
    - Comprehensive result reporting (stdout, stderr, return code, execution time)
    - CLI/GUI execution strategies
    - Callback support for lifecycle events
    - Timeout handling
    - Process management (kill, wait)
    """

    def __init__(
        self,
        args: List[str],
        command_type: CommandType = CommandType.CLI,
        blocking: bool = True,
        timeout: Optional[float] = None,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        on_start: Optional[Callable[['AsyncCommand'], None]] = None,
        on_complete: Optional[Callable[['AsyncCommand', CommandExecutionResult], None]] = None,
        on_error: Optional[Callable[['AsyncCommand', Exception], None]] = None,
    ):
        """
        Initialize the AsyncCommand.

        Args:
            args: Command arguments as a list of strings
            command_type: Type of command (CLI or GUI)
            blocking: Whether the command should block execution (always True for async)
            timeout: Timeout in seconds (None for no timeout)
            cwd: Working directory for command execution
            env: Environment variables for command execution
            on_start: Callback called when command starts
            on_complete: Callback called when command completes
            on_error: Callback called when command fails
        """
        self.args = args
        self.command_type = command_type
        self.blocking = blocking  # Always True for async, kept for compatibility
        self.timeout = timeout
        self.cwd = Path(cwd) if cwd else None
        self.env = env or {}
        self.on_start = on_start
        self.on_complete = on_complete
        self.on_error = on_error

        # State management
        self._state = CommandState.PENDING
        self._process: Optional[subprocess.Popen] = None
        self._result: Optional[CommandExecutionResult] = None
        self._start_time: Optional[datetime] = None

        # Logger
        self.logger = get_logger(__name__)

    @property
    def state(self) -> CommandState:
        """Get the current state of the command."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Check if the command is currently running."""
        return self._state == CommandState.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if the command has completed (successfully or not)."""
        return self._state in [CommandState.COMPLETED, CommandState.FAILED, CommandState.TIMEOUT, CommandState.KILLED]

    @property
    def result(self) -> Optional[CommandExecutionResult]:
        """Get the execution result if available."""
        return self._result

    async def execute(self, timeout: Optional[float] = None) -> CommandExecutionResult:
        """
        Execute the command asynchronously.

        Args:
            timeout: Override the default timeout for this execution

        Returns:
            CommandExecutionResult: Comprehensive execution result

        Raises:
            RuntimeError: If command is not in pending state
        """
        # Log command execution start
        self.logger.info("Executing command (async)", extra={
            "data": {
                "command": " ".join(self.args),
                "command_args": self.args,
                "command_type": self.command_type.value,
                "blocking": self.blocking,
                "timeout": timeout or self.timeout,
                "cwd": str(self.cwd) if self.cwd else None,
                "env_keys": list(self.env.keys()) if self.env else None
            }
        })

        # Check if command is in pending state
        if self._state != CommandState.PENDING:
            raise RuntimeError(f"Command is not in pending state: {self._state}")

        # Set initial state
        self._state = CommandState.RUNNING
        self._start_time = datetime.now()

        # Call on_start callback
        if self.on_start:
            self.on_start(self)

        try:
            # Execute based on command type
            if self.command_type == CommandType.CLI:
                result = await self._execute_cli_strategy(timeout)
            else:
                result = await self._execute_gui_strategy(timeout)

            return result

        except (OSError, ValueError, subprocess.SubprocessError, asyncio.TimeoutError) as e:
            # Handle unexpected errors
            end_time = datetime.now()
            execution_time = (end_time - self._start_time).total_seconds()

            result = CommandExecutionResult(
                command=self,
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Command execution failed: {str(e)}",
                execution_time=execution_time,
                state=CommandState.FAILED,
                start_time=self._start_time,
                end_time=end_time,
                command_type=self.command_type,
                exception=e
            )

            self._state = CommandState.FAILED
            self._result = result

            if self.on_error:
                self.on_error(self, e)

            return result

    async def _execute_cli_strategy(self, timeout: Optional[float] = None) -> CommandExecutionResult:
        """Execute using CLI strategy asynchronously."""
        start_time = self._start_time or datetime.now()
        effective_timeout = timeout if timeout is not None else self.timeout

        try:
            # Create subprocess
            # Merge environment variables with current environment
            env = os.environ.copy()
            if self.env:
                env.update(self.env)

            self._process = subprocess.Popen(
                self.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                cwd=str(self.cwd) if self.cwd else None,
                env=env
            )

            pid = self._process.pid
            self.logger.debug("CLI subprocess created (async)", extra={
                "data": {
                    "pid": pid,
                    "command": " ".join(self.args),
                    "timeout": effective_timeout
                }
            })

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    asyncio.to_thread(self._process.communicate),
                    timeout=effective_timeout
                )
                returncode = self._process.returncode

                if returncode == 0:
                    self.logger.info("CLI subprocess completed successfully (async)", extra={
                        "data": {
                            "pid": pid,
                            "command": " ".join(self.args),
                            "returncode": returncode,
                            "stdout_length": len(stdout),
                            "stderr_length": len(stderr)
                        }
                    })
                else:
                    self.logger.warning("CLI subprocess completed with non-zero exit code (async)", extra={
                        "data": {
                            "pid": pid,
                            "command": " ".join(self.args),
                            "returncode": returncode,
                            "stderr_length": len(stderr)
                        }
                    })

            except asyncio.TimeoutError:
                # Kill the process on timeout
                self.logger.warning("CLI subprocess timed out, killing process (async)", extra={
                    "data": {
                        "pid": pid,
                        "command": " ".join(self.args),
                        "timeout": effective_timeout
                    }
                })

                try:
                    self._process.kill()
                    stdout, stderr = await asyncio.to_thread(self._process.communicate)
                except (OSError, subprocess.SubprocessError, BaseException):
                    stdout, stderr = "", ""
                returncode = -1

                self.logger.error("CLI subprocess killed due to timeout (async)", extra={
                    "data": {
                        "pid": pid,
                        "command": " ".join(self.args),
                        "timeout": effective_timeout,
                        "stderr_length": len(stderr),
                        "stdout_length": len(stdout)
                    }
                })

                # Set timeout state and return early
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()

                result = CommandExecutionResult(
                    command=self,
                    success=False,
                    return_code=returncode,
                    stdout=stdout or "",
                    stderr=stderr or "",
                    execution_time=execution_time,
                    state=CommandState.TIMEOUT,
                    timeout_occurred=True,
                    start_time=start_time,
                    end_time=end_time,
                    pid=pid,
                    command_type=self.command_type
                )

                self._state = CommandState.TIMEOUT
                self._result = result

                if self.on_complete:
                    self.on_complete(self, result)

                return result

        except (OSError, ValueError, subprocess.SubprocessError) as e:
            returncode = -1
            stdout = ""
            stderr = f"CLI command failed to start: {str(e)}"

            self.logger.error("CLI subprocess execution failed (async)", extra={
                "data": {
                    "command": " ".join(self.args),
                    "error": str(e),
                    "timeout": effective_timeout
                }
            })

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        success = returncode == 0
        state = CommandState.COMPLETED if success else CommandState.FAILED

        # Check if this was a timeout
        timeout_occurred = False
        if returncode == -1 and effective_timeout is not None and execution_time >= effective_timeout * 0.9:
            state = CommandState.TIMEOUT
            timeout_occurred = True

        result = CommandExecutionResult(
            command=self,
            success=success,
            return_code=returncode,
            stdout=stdout or "",
            stderr=stderr or "",
            execution_time=execution_time,
            state=state,
            timeout_occurred=timeout_occurred,
            start_time=start_time,
            end_time=end_time,
            pid=self._process.pid if self._process else None,
            command_type=self.command_type
        )

        self._state = state
        self._result = result

        # Call appropriate callback based on result
        if not success and self.on_error:
            # Create a generic exception for non-zero return codes
            error = RuntimeError(f"Command failed with return code {returncode}")
            self.on_error(self, error)
        elif self.on_complete:
            self.on_complete(self, result)

        return result

    async def _execute_gui_strategy(self, timeout: Optional[float] = None) -> CommandExecutionResult:
        """Execute using GUI strategy asynchronously."""
        start_time = self._start_time or datetime.now()
        effective_timeout = timeout if timeout is not None else self.timeout

        try:
            # Create subprocess without capturing output
            # Merge environment variables with current environment
            env = os.environ.copy()
            if self.env:
                env.update(self.env)

            self._process = subprocess.Popen(
                self.args,
                shell=True,
                cwd=str(self.cwd) if self.cwd else None,
                env=env
            )

            pid = self._process.pid
            self.logger.debug("GUI subprocess created (async)", extra={
                "data": {
                    "pid": pid,
                    "command": " ".join(self.args),
                    "timeout": effective_timeout
                }
            })

            # Wait for completion with timeout
            try:
                returncode = await asyncio.wait_for(
                    asyncio.to_thread(self._process.wait),
                    timeout=effective_timeout
                )

                if returncode == 0:
                    self.logger.info("GUI subprocess completed successfully (async)", extra={
                        "data": {
                            "pid": pid,
                            "command": " ".join(self.args),
                            "returncode": returncode
                        }
                    })
                else:
                    self.logger.warning("GUI subprocess completed with non-zero exit code (async)", extra={
                        "data": {
                            "pid": pid,
                            "command": " ".join(self.args),
                            "returncode": returncode
                        }
                    })

            except asyncio.TimeoutError:
                # Kill the process on timeout
                self.logger.warning("GUI subprocess timed out, killing process (async)", extra={
                    "data": {
                        "pid": pid,
                        "command": " ".join(self.args),
                        "timeout": effective_timeout
                    }
                })

                try:
                    self._process.kill()
                    await asyncio.to_thread(self._process.wait)
                except (OSError, subprocess.SubprocessError, BaseException):
                    pass
                returncode = -1

                self.logger.error("GUI subprocess killed due to timeout (async)", extra={
                    "data": {
                        "pid": pid,
                        "command": " ".join(self.args),
                        "timeout": effective_timeout
                    }
                })

                # Set timeout state and return early
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()

                result = CommandExecutionResult(
                    command=self,
                    success=False,
                    return_code=returncode,
                    stdout="",  # GUI commands don't capture output
                    stderr="",  # GUI commands don't capture output
                    execution_time=execution_time,
                    state=CommandState.TIMEOUT,
                    timeout_occurred=True,
                    start_time=start_time,
                    end_time=end_time,
                    pid=pid,
                    command_type=self.command_type
                )

                self._state = CommandState.TIMEOUT
                self._result = result

                if self.on_complete:
                    self.on_complete(self, result)

                return result

        except (OSError, ValueError, subprocess.SubprocessError) as e:
            returncode = -1
            self.logger.error("GUI subprocess execution failed (async)", extra={
                "data": {
                    "command": " ".join(self.args),
                    "error": str(e),
                    "timeout": effective_timeout
                }
            })

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        success = returncode == 0
        state = CommandState.COMPLETED if success else CommandState.FAILED

        # Check if this was a timeout
        timeout_occurred = False
        if returncode == -1 and effective_timeout is not None and execution_time >= effective_timeout * 0.9:
            state = CommandState.TIMEOUT
            timeout_occurred = True

        result = CommandExecutionResult(
            command=self,
            success=success,
            return_code=returncode,
            stdout="",  # GUI commands don't capture output
            stderr="",  # GUI commands don't capture output
            execution_time=execution_time,
            state=state,
            timeout_occurred=timeout_occurred,
            start_time=start_time,
            end_time=end_time,
            pid=self._process.pid if self._process else None,
            command_type=self.command_type
        )

        self._state = state
        self._result = result

        # Call appropriate callback based on result
        if not success and self.on_error:
            # Create a generic exception for non-zero return codes
            error = RuntimeError(f"Command failed with return code {returncode}")
            self.on_error(self, error)
        elif self.on_complete:
            self.on_complete(self, result)

        return result

    def kill(self) -> bool:
        """
        Kill the running command.

        Returns:
            bool: True if the command was killed, False otherwise
        """
        self.logger.info("Attempting to kill command", extra={
            "data": {
                "command": " ".join(self.args),
                "state": self._state.value,
                "has_process": self._process is not None
            }
        })

        if not self._process or not self.is_running:
            self.logger.warning("Attempted to kill command that is not running", extra={
                "data": {
                    "command": " ".join(self.args),
                    "state": self._state.value,
                    "has_process": self._process is not None,
                    "is_running": self.is_running
                }
            })
            return False

        pid = self._process.pid
        try:
            self._process.kill()
            self._state = CommandState.KILLED

            self.logger.info("Command killed successfully", extra={
                "data": {
                    "command": " ".join(self.args),
                    "pid": pid,
                    "state": self._state.value
                }
            })
            return True
        except (OSError, subprocess.SubprocessError) as e:
            self.logger.error("Failed to kill command", extra={
                "data": {
                    "command": " ".join(self.args),
                    "pid": pid,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            })
            return False

    async def wait(self) -> CommandExecutionResult:
        """
        Wait for the command to complete.

        Returns:
            CommandExecutionResult: The execution result
        """
        self.logger.info("Waiting for command to complete", extra={
            "data": {
                "command": " ".join(self.args),
                "state": self._state.value
            }
        })

        if self._result:
            self.logger.debug("Command already completed, returning cached result", extra={
                "data": {
                    "command": " ".join(self.args),
                    "state": self._state.value,
                    "success": self._result.success
                }
            })
            return self._result

        # If not running, execute first
        if self._state == CommandState.PENDING:
            return await self.execute()

        # Wait for completion
        while not self.is_completed:
            await asyncio.sleep(0.1)

        self.logger.info("Command completed", extra={
            "data": {
                "command": " ".join(self.args),
                "state": self._state.value,
                "success": self._result.success if self._result else False
            }
        })

        return self._result

    def to_command_result(self) -> CommandResult:
        """Convert to CommandResult schema."""
        if not self._result:
            return CommandResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr="Command not executed",
                execution_time=0.0
            )

        return CommandResult(
            success=self._result.success,
            return_code=self._result.return_code,
            stdout=self._result.stdout,
            stderr=self._result.stderr,
            execution_time=self._result.execution_time
        )

    def to_command_response(self) -> CommandResponse:
        """Convert to CommandResponse schema."""
        if not self._result:
            return CommandResponse(
                success=False,
                message="Command not executed",
                data={}
            )

        return CommandResponse(
            success=self._result.success,
            message="Command executed successfully" if self._result.success else "Command failed",
            data={
                "return_code": self._result.return_code,
                "stdout": self._result.stdout,
                "stderr": self._result.stderr,
                "execution_time": self._result.execution_time,
                "state": self._state.value,
                "pid": self._result.pid
            }
        )

    @staticmethod
    def shell(command: str, **kwargs) -> 'AsyncCommand':
        """
        Create a shell command.

        Args:
            command: Shell command string
            **kwargs: Additional arguments for AsyncCommand

        Returns:
            AsyncCommand: Configured command instance
        """
        return AsyncCommand(
            args=[command],
            command_type=CommandType.CLI,
            **kwargs
        )

    def __repr__(self) -> str:
        """String representation of the command."""
        return f"AsyncCommand(args={self.args}, state={self._state.value})"


# Backward compatibility alias
Command = AsyncCommand
