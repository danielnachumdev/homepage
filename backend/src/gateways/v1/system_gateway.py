import asyncio
import subprocess
from typing import Optional
from ...schemas.v1.system import CommandResponse


class SystemGateway:
    """Gateway for executing system commands asynchronously."""

    @staticmethod
    async def execute_command(command: str) -> CommandResponse:
        """Execute a system command asynchronously."""
        try:
            # Run the command asynchronously
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # Decode output
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            error = stderr.decode('utf-8', errors='ignore') if stderr else ""

            return CommandResponse(
                success=process.returncode == 0,
                output=output,
                error=error if process.returncode != 0 else None
            )

        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )

    @staticmethod
    async def execute_command_with_timeout(command: str, timeout: float = 30.0) -> CommandResponse:
        """Execute a system command asynchronously with a timeout."""
        try:
            # Run the command asynchronously with timeout
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
                process.kill()
                await process.wait()
                return CommandResponse(
                    success=False,
                    output="",
                    error=f"Command timed out after {timeout} seconds"
                )

            # Decode output
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            error = stderr.decode('utf-8', errors='ignore') if stderr else ""

            return CommandResponse(
                success=process.returncode == 0,
                output=output,
                error=error if process.returncode != 0 else None
            )

        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )

    @staticmethod
    async def execute_multiple_commands(commands: list[str], max_concurrent: int = 5) -> list[CommandResponse]:
        """Execute multiple commands concurrently with a limit on concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(cmd: str) -> CommandResponse:
            async with semaphore:
                return await SystemGateway.execute_command(cmd)

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
