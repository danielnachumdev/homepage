import asyncio
import subprocess
import shlex
from datetime import datetime
from typing import Optional, Union, List
from ...schemas.v1.system import CommandResponse, CommandResult
from ...utils.logger import get_logger


def _execute_subprocess(args: List[str], command: str, timeout: Optional[float] = None) -> CommandResult:
    """Private global function to execute subprocess with comprehensive result tracking."""
    logger = get_logger(__name__)

    start_time = datetime.now()
    start_time_str = start_time.isoformat()

    logger.info("Starting subprocess execution", extra={
        "data": {
            "command": command,
            "command_args": args,
            "timeout": timeout,
            "start_time": start_time_str
        }
    })

    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    pid = process.pid
    timeout_occurred = False
    killed = False

    logger.debug("Subprocess created", extra={
        "data": {
            "pid": pid,
            "command": command
        }
    })

    try:
        # Only apply timeout if it's a reasonable positive number (> 0.01 seconds)
        if timeout is not None and timeout > 0.01:
            logger.debug("Waiting for subprocess with timeout", extra={
                "data": {
                    "pid": pid,
                    "timeout": timeout,
                    "command": command
                }
            })
            stdout, stderr = process.communicate(timeout=timeout)
        else:
            logger.debug("Waiting for subprocess without timeout", extra={
                "data": {
                    "pid": pid,
                    "command": command
                }
            })
            stdout, stderr = process.communicate()
        returncode = process.returncode

        logger.info("Subprocess completed successfully", extra={
            "data": {
                "pid": pid,
                "returncode": returncode,
                "command": command,
                "stdout_length": len(stdout) if stdout else 0,
                "stderr_length": len(stderr) if stderr else 0
            }
        })

    except subprocess.TimeoutExpired:
        logger.warning("Subprocess timed out, killing process", extra={
            "data": {
                "pid": pid,
                "timeout": timeout,
                "command": command
            }
        })
        process.kill()
        stdout, stderr = process.communicate()
        returncode = -1
        timeout_occurred = True
        killed = True
        stderr = f"Command timed out after {timeout} seconds"

        logger.error("Subprocess killed due to timeout", extra={
            "data": {
                "pid": pid,
                "timeout": timeout,
                "command": command,
                "stdout_length": len(stdout) if stdout else 0,
                "stderr_length": len(stderr) if stderr else 0
            }
        })

    end_time = datetime.now()
    end_time_str = end_time.isoformat()
    duration_seconds = (end_time - start_time).total_seconds()

    result = CommandResult(
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

    logger.info("Subprocess execution completed", extra={
        "data": {
            "pid": pid,
            "command": command,
            "success": result.success,
            "duration_seconds": duration_seconds,
            "timeout_occurred": timeout_occurred,
            "killed": killed,
            "returncode": returncode
        }
    })

    return result


class SystemGateway:
    """Gateway for executing system commands asynchronously."""

    def __init__(self):
        self.logger = get_logger(__name__)

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
    async def _execute_command_internal(args: List[str], timeout: Optional[float] = None) -> CommandResponse:
        """Internal method to execute a command with given arguments."""
        logger = get_logger(__name__)
        command_str = " ".join(args)

        logger.info("Starting command execution", extra={
            "data": {
                "command": command_str,
                "command_args": args,
                "timeout": timeout
            }
        })

        try:
            # Use asyncio.to_thread for better cross-platform compatibility
            # Only apply asyncio timeout if it's a reasonable positive number (> 0.01 seconds)
            if timeout is not None and timeout > 0.01:
                logger.debug("Executing command with asyncio timeout", extra={
                    "data": {
                        "command": command_str,
                        "timeout": timeout
                    }
                })
                result = await asyncio.wait_for(
                    asyncio.to_thread(_execute_subprocess, args, command_str, timeout),
                    timeout=timeout
                )
            else:
                logger.debug("Executing command without asyncio timeout", extra={
                    "data": {
                        "command": command_str
                    }
                })
                result = await asyncio.to_thread(_execute_subprocess, args, command_str, timeout)

            return CommandResponse(
                success=result.success,
                output=result.stdout or "",
                error=result.stderr if not result.success else None,
                result=result
            )

        except asyncio.TimeoutError:
            logger.error("Command execution timed out at asyncio level", extra={
                "data": {
                    "command": command_str,
                    "timeout": timeout
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
            logger.error("Command execution failed with exception", extra={
                "data": {
                    "command": command_str,
                    "error": str(e),
                    "error_type": type(e).__name__
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
    async def execute_multiple_commands(
            commands: list[Union[str, list[str]]], max_concurrent: int = 5) -> list[CommandResponse]:
        """Execute multiple commands concurrently with a limit on concurrency."""
        logger = get_logger(__name__)

        # Validate max_concurrent parameter
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
