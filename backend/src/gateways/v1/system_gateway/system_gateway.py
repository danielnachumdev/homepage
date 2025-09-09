import asyncio
import shlex
from typing import Optional, Union, List
from ....schemas.v1.system import CommandResponse
from ....utils.logger import get_logger
from .command_executor import CommandExecutor

logger = get_logger(__name__)


class SystemGateway:
    """Gateway for executing system commands asynchronously."""

    @staticmethod
    def _parse_command(command: str) -> list[str]:
        """Parse a command string into a list of arguments, handling basic quoting."""
        logger = get_logger(__name__)

        logger.debug("Parsing command string", extra={
            "data": {
                "command": command
            }
        })

        try:
            # Use shlex to properly parse the command, handling quotes and escaping
            args = shlex.split(command)
            logger.debug("Command parsed successfully with shlex", extra={
                "data": {
                    "command": command,
                    "command_args": args
                }
            })
            return args
        except ValueError as e:
            # Fallback to simple split if shlex fails
            logger.warning("shlex parsing failed, using simple split", extra={
                "data": {
                    "command": command,
                    "error": str(e)
                }
            })
            args = command.split()
            logger.debug("Command parsed with simple split", extra={
                "data": {
                    "command": command,
                    "command_args": args
                }
            })
            return args

    @staticmethod
    async def kill_process(pid: int) -> bool:
        """Kill a process by PID."""
        try:
            command = f"taskkill /PID {pid} /F"
            result = await SystemGateway.execute_command(command)

            if result.success:
                logger.info("Successfully killed process", extra={
                    "data": {
                        "pid": pid
                    }
                })
                return True
            else:
                logger.warning("Failed to kill process", extra={
                    "data": {
                        "pid": pid,
                        "error": result.error
                    }
                })
                return False

        except Exception as e:
            logger.error("Error killing process", extra={
                "data": {
                    "pid": pid,
                    "error": str(e)
                }
            })
            return False

    @staticmethod
    async def execute_command_args(
            args: List[str],
            timeout: Optional[float] = None,
            is_cli: bool = True
    ) -> CommandResponse:
        """Execute a system command using a list of arguments directly."""
        return await CommandExecutor().execute_command(args, timeout, is_cli)

    @staticmethod
    async def execute_command(
            command: str,
            timeout: Optional[float] = None,
            is_cli: bool = True
    ) -> CommandResponse:
        """Execute a system command asynchronously from a string."""
        args = SystemGateway._parse_command(command)
        return await SystemGateway.execute_command_args(args, timeout, is_cli)

    @staticmethod
    async def execute_multiple_commands(
            commands: list[Union[str, list[str]]],
            max_concurrent: int = 5
    ) -> list[CommandResponse]:
        """Execute multiple commands concurrently with a limit on concurrency."""
        if max_concurrent <= 0:
            raise ValueError(f"max_concurrent must be a strictly positive integer, got: {max_concurrent}")

        logger.info("Starting multiple command execution", extra={
            "data": {
                "command_count": len(commands),
                "max_concurrent": max_concurrent
            }
        })

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
        exception_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Command execution failed in multiple commands", extra={
                    "data": {
                        "command_index": i,
                        "command": commands[i],
                        "error": str(result),
                        "error_type": type(result).__name__
                    }
                })
                responses.append(CommandResponse(
                    success=False,
                    output="",
                    error=f"Command execution failed: {str(result)}"
                ))
                exception_count += 1
            else:
                responses.append(result)

        logger.info("Multiple command execution completed", extra={
            "data": {
                "total_commands": len(commands),
                "successful_commands": len(commands) - exception_count,
                "failed_commands": exception_count,
                "max_concurrent": max_concurrent
            }
        })

        return responses


__all__ = [
    "SystemGateway"
]
