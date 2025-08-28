import asyncio
import subprocess
import shlex
from typing import Optional, Union
from ...schemas.v1.system import CommandResponse


class SystemGateway:
    """Gateway for executing system commands asynchronously."""

    @staticmethod
    def _parse_command(command: str) -> list[str]:
        """Parse a command string into a list of arguments, handling basic quoting."""
        try:
            # Use shlex to properly parse the command, handling quotes and escaping
            return shlex.split(command)
        except ValueError:
            # Fallback to simple split if shlex fails
            return command.split()

    @staticmethod
    async def _execute_command_internal(args: list[str], timeout: Optional[float] = None) -> CommandResponse:
        """Internal method to execute a command with given arguments."""
        try:
            coro = asyncio.to_thread(
                subprocess.run,
                args,
                capture_output=True,
                text=True,
                check=False
            )
            # Use asyncio.to_thread with subprocess.run for better cross-platform compatibility
            if timeout:
                # For timeout support, we need to handle it manually since subprocess.run doesn't support it natively
                # We'll use asyncio.wait_for with the subprocess call
                result = await asyncio.wait_for(
                    coro,
                    timeout=timeout
                )
            else:
                result = await coro

            return CommandResponse(
                success=result.returncode == 0,
                output=result.stdout or "",
                error=result.stderr if result.returncode != 0 else None
            )

        except asyncio.TimeoutError:
            return CommandResponse(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )

    @staticmethod
    async def execute_command_args(args: list[str]) -> CommandResponse:
        """Execute a system command using a list of arguments directly."""
        return await SystemGateway._execute_command_internal(args)

    @staticmethod
    async def execute_command(command: str) -> CommandResponse:
        """Execute a system command asynchronously from a string."""
        args = SystemGateway._parse_command(command)
        return await SystemGateway._execute_command_internal(args)

    @staticmethod
    async def execute_command_with_timeout(command: str, timeout: float = 30.0) -> CommandResponse:
        """Execute a system command asynchronously with a timeout."""
        args = SystemGateway._parse_command(command)
        return await SystemGateway._execute_command_internal(args, timeout)

    @staticmethod
    async def execute_command_args_with_timeout(args: list[str], timeout: float = 30.0) -> CommandResponse:
        """Execute a system command using a list of arguments with a timeout."""
        return await SystemGateway._execute_command_internal(args, timeout)

    @staticmethod
    async def execute_multiple_commands(commands: list[Union[str, list[str]]], max_concurrent: int = 5) -> list[CommandResponse]:
        """Execute multiple commands concurrently with a limit on concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(cmd: Union[str, list[str]]) -> CommandResponse:
            async with semaphore:
                if isinstance(cmd, str):
                    return await SystemGateway.execute_command(cmd)
                else:
                    return await SystemGateway.execute_command_args(cmd)

        # Execute all commands concurrently
        tasks = [execute_with_semaphore(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions that occurred
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append(CommandResponse(
                    success=False,
                    output="",
                    error=f"Command execution failed: {str(result)}"
                ))
            else:
                responses.append(result)

        return responses


__all__ = [
    "SystemGateway"
]
