import asyncio
import subprocess
from datetime import datetime
from typing import List, Optional

from .command_execution_strategy import CommandExecutionStrategy
from .strategies import CLICommandStrategy, GUICommandStrategy
from ....schemas.v1.system import CommandResponse, CommandResult
from ....utils.logger import get_logger


class CommandExecutor:
    """Command executor that uses strategy pattern to execute commands."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._cli_strategy = CLICommandStrategy()
        self._gui_strategy = GUICommandStrategy()

    def _select_strategy(self, is_cli: bool) -> CommandExecutionStrategy:
        """Select the appropriate strategy based on command type."""
        return self._cli_strategy if is_cli else self._gui_strategy

    async def execute_command(self, args: List[str], timeout: Optional[float] = None,
                              is_cli: bool = True) -> CommandResponse:
        """Execute a command using the appropriate strategy."""
        strategy = self._select_strategy(is_cli)
        command_str = " ".join(args)

        self.logger.info("Executing command with strategy", extra={
            "data": {
                "command": command_str,
                "command_args": args,
                "timeout": timeout,
                "is_cli": is_cli,
                "strategy": strategy.__class__.__name__
            }
        })

        try:
            # Use asyncio.to_thread for better cross-platform compatibility
            if timeout is not None and timeout > 0.01:
                result = await asyncio.wait_for(
                    asyncio.to_thread(strategy.execute, args, timeout),
                    timeout=timeout
                )
            else:
                result = await asyncio.to_thread(strategy.execute, args, timeout)

            return CommandResponse(
                success=result.success,
                output=result.stdout or "",
                error=result.stderr if not result.success else None,
                result=result
            )

        except asyncio.TimeoutError:
            self.logger.error("Command execution timed out at asyncio level", extra={
                "data": {
                    "command": command_str,
                    "timeout": timeout,
                    "is_cli": is_cli
                }
            })

            # Create a timeout CommandResult
            timeout_result = CommandResult(
                args=args,
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                pid=-1,
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                duration_seconds=0.0,
                timeout_occurred=True,
                killed=False,
                success=False,
                command=command_str
            )

            return CommandResponse(
                success=False,
                output="",
                error=timeout_result.stderr,
                result=timeout_result
            )

        except Exception as e:
            self.logger.error("Command execution failed with exception", extra={
                "data": {
                    "command": command_str,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "is_cli": is_cli
                }
            })

            # Create an error CommandResult
            error_result = CommandResult(
                args=args,
                returncode=-1,
                stdout="",
                stderr=str(e),
                pid=-1,
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                duration_seconds=0.0,
                timeout_occurred=False,
                killed=False,
                success=False,
                command=command_str
            )

            return CommandResponse(
                success=False,
                output="",
                error=error_result.stderr,
                result=error_result
            )

    async def execute_cli_command(self, args: List[str], timeout: Optional[float] = None) -> CommandResponse:
        """Execute a CLI command directly."""
        return await self.execute_command(args, timeout, is_cli=True)

    async def execute_gui_command(self, args: List[str], timeout: Optional[float] = None) -> CommandResponse:
        """Execute a GUI command directly."""
        return await self.execute_command(args, timeout, is_cli=False)


__all__ = [
    "CommandExecutor"
]
