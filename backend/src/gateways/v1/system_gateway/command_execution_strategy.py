from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ....utils import get_logger
from ....schemas import CommandResult


class CommandExecutionStrategy(ABC):
    """Abstract base class for command execution strategies."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def _create_common_result(self, args: List[str], command: str, start_time: datetime,
                              end_time: datetime, pid: int, returncode: int,
                              stdout: str, stderr: str, timeout_occurred: bool = False,
                              killed: bool = False) -> CommandResult:
        """Create a CommandResult with common fields."""
        duration_seconds = (end_time - start_time).total_seconds()
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()

        return CommandResult(
            args=args,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            pid=pid,
            start_time=start_time_str,
            end_time=end_time_str,
            duration_seconds=duration_seconds,
            timeout_occurred=timeout_occurred,
            killed=killed,
            success=returncode == 0,
            command=command
        )

    def _log_execution_start(self, command: str, args: List[str], timeout: Optional[float],
                             start_time: datetime) -> None:
        """Log the start of command execution."""
        self.logger.info("Starting command execution", extra={
            "data": {
                "command": command,
                "command_args": args,
                "timeout": timeout,
                "start_time": start_time.isoformat(),
                "strategy": self.__class__.__name__
            }
        })

    def _log_execution_complete(self, command: str, pid: int, result: CommandResult) -> None:
        """Log the completion of command execution."""
        self.logger.info("Command execution completed", extra={
            "data": {
                "pid": pid,
                "command": command,
                "success": result.success,
                "duration_seconds": result.duration_seconds,
                "timeout_occurred": result.timeout_occurred,
                "killed": result.killed,
                "returncode": result.returncode,
                "strategy": self.__class__.__name__
            }
        })

    @abstractmethod
    def execute(self, args: List[str], timeout: Optional[float] = None) -> CommandResult:
        """Execute a command using this strategy."""
        pass


__all__ = [
    "CommandExecutionStrategy",
]
