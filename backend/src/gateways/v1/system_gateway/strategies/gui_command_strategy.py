import subprocess
import time
from datetime import datetime
from typing import List, Optional

from ..command_execution_strategy import CommandExecutionStrategy
from .....schemas.v1.system import CommandResult


class GUICommandStrategy(CommandExecutionStrategy):
    """Strategy for executing GUI commands with fire-and-forget behavior."""

    def execute(self, args: List[str], timeout: Optional[float] = None) -> CommandResult:
        """Execute a GUI command with fire-and-forget behavior."""
        command = " ".join(args)
        start_time = datetime.now()

        self._log_execution_start(command, args, timeout, start_time)

        process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )

        pid = process.pid
        timeout_occurred = False
        killed = False

        self.logger.debug("GUI subprocess created", extra={
            "data": {
                "pid": pid,
                "command": command
            }
        })

        try:
            # Give the process a moment to start up
            time.sleep(0.5)

            # Check if process is still running (started successfully)
            if process.poll() is None:
                # Process is still running, which is expected for GUI apps
                returncode = 0
                stdout = ""
                stderr = ""
                self.logger.info("GUI application started successfully", extra={
                    "data": {
                        "pid": pid,
                        "command": command,
                        "returncode": returncode
                    }
                })
            else:
                # Process exited quickly, might be an error
                returncode = process.returncode
                stdout = ""
                stderr = f"GUI application exited immediately with return code {returncode}"
                self.logger.warning("GUI application exited immediately", extra={
                    "data": {
                        "pid": pid,
                        "command": command,
                        "returncode": returncode
                    }
                })

        except Exception as e:
            # Handle any unexpected errors during GUI process startup
            self.logger.error("GUI subprocess execution failed", extra={
                "data": {
                    "pid": pid,
                    "command": command,
                    "error": str(e)
                }
            })
            returncode = -1
            stdout = ""
            stderr = f"GUI application failed to start: {str(e)}"

        end_time = datetime.now()
        result = self._create_common_result(
            args, command, start_time, end_time, pid, returncode,
            stdout, stderr, timeout_occurred, killed
        )

        self._log_execution_complete(command, pid, result)
        return result


__all__ = [
    "GUICommandStrategy"
]
