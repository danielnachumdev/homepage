import subprocess
from ...schemas.v1.system import CommandResponse


class SystemGateway:
    """Gateway for executing system commands with proper validation and error handling."""

    @staticmethod
    def execute_command(command: str) -> CommandResponse:
        """Execute a system command using subprocess with timeout and error handling"""
        try:
            # Use subprocess for better output capture and security
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout for safety
            )

            if result.returncode == 0:
                return CommandResponse(
                    success=True,
                    output=result.stdout,
                    error=None
                )
            else:
                return CommandResponse(
                    success=False,
                    output=result.stdout,
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return CommandResponse(
                success=False,
                output="",
                error="Command timed out after 30 seconds"
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )


__all__ = [
    "SystemGateway"
]
