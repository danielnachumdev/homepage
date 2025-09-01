"""
Command-based execution system for deployment steps.

This module provides the Command dataclass and related utilities for
declarative command execution in deployment steps.
"""

from dataclasses import dataclass
from typing import Optional, Any, Union, List
from pathlib import Path


@dataclass
class Command:
    """
    Represents a single command to be executed.

    This class encapsulates all the information needed to execute a command,
    including the command itself, execution parameters, and expected outcomes.
    """

    command: Union[str, List[str]]
    """The command to execute (string or list of strings)"""

    required: bool = True
    """Whether this command is required for the step to succeed"""

    retry_count: Optional[int] = None
    """Number of times to retry this command if it fails (None = no retries)"""

    expected: Optional[Any] = None
    """Expected return code or output pattern for validation"""

    cwd: Optional[Union[str, Path]] = None
    """Working directory for the command"""

    description: Optional[str] = None
    """Human-readable description of what this command does"""

    timeout: Optional[float] = None
    """Timeout in seconds for command execution"""

    def __post_init__(self):
        """Validate command after initialization."""
        if not self.command:
            raise ValueError("Command cannot be empty")

        if self.retry_count is not None and self.retry_count < 0:
            raise ValueError("Retry count must be non-negative")


@dataclass
class CommandResult:
    """
    Result of executing a single command.

    This class contains the execution results and metadata for a command.
    """

    command: Command
    """The command that was executed"""

    success: bool
    """Whether the command executed successfully"""

    return_code: int
    """The return code of the command"""

    stdout: str
    """Standard output from the command"""

    stderr: str
    """Standard error from the command"""

    execution_time: float
    """Time taken to execute the command in seconds"""

    retry_count: int = 0
    """Number of retries attempted"""

    error_message: Optional[str] = None
    """Error message if the command failed"""

    def is_expected_result(self) -> bool:
        """
        Check if the command result matches the expected outcome.

        Returns:
            bool: True if the result matches expectations, False otherwise
        """
        if self.command.expected is None:
            return self.success

        # If expected is an integer, check return code
        if isinstance(self.command.expected, int):
            return self.return_code == self.command.expected

        # If expected is a string, check if it appears in stdout or stderr
        if isinstance(self.command.expected, str):
            return (self.command.expected in self.stdout or
                    self.command.expected in self.stderr)

        # For other types, just check success
        return self.success


@dataclass
class StepExecutionResult:
    """
    Result of executing all commands in a step.

    This class contains the results of executing all commands in a step,
    along with overall step status and metadata.
    """

    step_name: str
    """Name of the step that was executed"""

    success: bool
    """Whether the step completed successfully"""

    command_results: List[CommandResult]
    """Results of all commands executed in this step"""

    total_execution_time: float
    """Total time taken to execute all commands"""

    failed_commands: List[CommandResult]
    """List of commands that failed"""

    error_message: Optional[str] = None
    """Overall error message if the step failed"""

    def get_failed_required_commands(self) -> List[CommandResult]:
        """
        Get list of failed commands that were marked as required.

        Returns:
            List of CommandResult objects for failed required commands
        """
        return [result for result in self.failed_commands
                if result.command.required]


__all__ = [
    "Command",
    "CommandResult",
    "StepExecutionResult"
]
