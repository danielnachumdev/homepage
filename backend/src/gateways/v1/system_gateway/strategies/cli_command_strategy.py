import subprocess
from datetime import datetime
from typing import List, Optional

from .....schemas import CommandResult
from ..command_execution_strategy import CommandExecutionStrategy


class CLICommandStrategy(CommandExecutionStrategy):
    """Strategy for executing CLI commands with output capture and timeout handling."""

    def execute(self, args: List[str], timeout: Optional[float] = None) -> CommandResult:
        """Execute a CLI command with full output capture."""
        command = " ".join(args)
        start_time = datetime.now()

        self._log_execution_start(command, args, timeout, start_time)

        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        pid = process.pid
        timeout_occurred = False
        killed = False

        self.logger.debug("CLI subprocess created", extra={
            "data": {
                "pid": pid,
                "command": command
            }
        })

        try:
            # Wait for completion and capture output
            if not (timeout is not None and timeout > 0.01):
                timeout = None
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode

            self.logger.info("CLI subprocess completed successfully", extra={
                "data": {
                    "pid": pid,
                    "returncode": returncode,
                    "command": command,
                    "stdout_length": len(stdout) if stdout else 0,
                    "stderr_length": len(stderr) if stderr else 0
                }
            })

        except subprocess.TimeoutExpired:
            self.logger.warning("CLI subprocess timed out, killing process", extra={
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

            self.logger.error("CLI subprocess killed due to timeout", extra={
                "data": {
                    "pid": pid,
                    "timeout": timeout,
                    "command": command,
                    "stdout_length": len(stdout) if stdout else 0,
                    "stderr_length": len(stderr) if stderr else 0
                }
            })

        end_time = datetime.now()
        result = self._create_common_result(
            args, command, start_time, end_time, pid, returncode,
            stdout, stderr, timeout_occurred, killed
        )

        self._log_execution_complete(command, pid, result)
        return result


__all__ = [
    "CLICommandStrategy"
]
