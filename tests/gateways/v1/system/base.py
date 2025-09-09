"""
Base test classes for system gateway testing.
"""
from typing import List, Optional
import platform

from backend.src.schemas.v1.system import CommandResponse, CommandResult
from ....base import BaseTest


class BaseSystemGatewayTest(BaseTest):
    """Base test class for all system gateway tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()

        # Platform-specific command helpers
        self.is_windows = platform.system() == "Windows"

    def get_echo_command(self, text: str) -> str:
        """Get platform-specific echo command."""
        if self.is_windows:
            return f'cmd /c echo "{text}"'
        else:
            return f'echo "{text}"'

    def get_echo_args(self, text: str) -> List[str]:
        """Get platform-specific echo command arguments."""
        if self.is_windows:
            return ["cmd", "/c", "echo", text]
        else:
            return ["echo", text]

    def get_sleep_command(self, seconds: int) -> str:
        """Get platform-specific sleep command."""
        if self.is_windows:
            return f'timeout /t {seconds} /nobreak'
        else:
            return f'sleep {seconds}'

    def get_sleep_args(self, seconds: int) -> List[str]:
        """Get platform-specific sleep command arguments."""
        if self.is_windows:
            return ["timeout", "/t", str(seconds), "/nobreak"]
        else:
            return ["sleep", str(seconds)]

    def get_invalid_command(self) -> str:
        """Get a command that will definitely fail."""
        return "nonexistent_command_that_should_fail_12345"

    def get_invalid_args(self) -> List[str]:
        """Get arguments for a command that will definitely fail."""
        return ["nonexistent_command_that_should_fail_12345"]

    def assertCommandResponse(self, response: CommandResponse,
                              expected_success: Optional[bool] = None,
                              expected_output_contains: Optional[List[str]] = None,
                              expected_error_contains: Optional[List[str]] = None,
                              result_should_be_completed: Optional[bool] = None,
                              result_should_be_running: Optional[bool] = None,
                              message: str = "") -> None:
        """Comprehensive assertion method for command responses with detailed error logging."""

        # Validate response structure
        self.assertIsInstance(response, CommandResponse)
        self.assertIsInstance(response.success, bool)
        self.assertIsInstance(response.output, str)

        # Check success/failure expectation
        if expected_success is not None:
            if expected_success and not response.success:
                error_msg = f"Command was expected to succeed but failed. "
                if response.error:
                    error_msg += f"Error: {response.error}. "
                if response.output:
                    error_msg += f"Output: {response.output}. "
                if message:
                    error_msg += f"Context: {message}"
                self.fail(error_msg)
            elif not expected_success and response.success:
                error_msg = f"Command was expected to fail but succeeded. "
                if response.output:
                    error_msg += f"Output: {response.output}. "
                if message:
                    error_msg += f"Context: {message}"
                self.fail(error_msg)

        # Check output content expectation
        if expected_output_contains and response.success:
            if not any(expected in response.output for expected in expected_output_contains if expected):
                error_msg = f"Command succeeded but output doesn't contain expected content. "
                error_msg += f"Expected one of: {expected_output_contains}. "
                error_msg += f"Actual output: '{response.output}'. "
                if message:
                    error_msg += f"Context: {message}"
                self.fail(error_msg)

        # Check error content expectation
        if expected_error_contains and not response.success:
            if not any(expected in (response.error or "") for expected in expected_error_contains if expected):
                error_msg = f"Command failed but error doesn't contain expected content. "
                error_msg += f"Expected one of: {expected_error_contains}. "
                error_msg += f"Actual error: '{response.error}'. "
                if message:
                    error_msg += f"Context: {message}"
                self.fail(error_msg)

        # Check result validation
        if response.result:
            self.assertCommandResult(
                response.result,
                should_be_completed=result_should_be_completed,
                should_be_running=result_should_be_running,
                message=message
            )

    def assertCommandResult(self, result: CommandResult,
                            should_be_completed: Optional[bool] = None,
                            should_be_running: Optional[bool] = None,
                            message: str = "") -> None:
        """Comprehensive assertion method for command results with detailed error logging."""

        # Validate result structure
        self.assertIsInstance(result, CommandResult)
        self.assertIsInstance(result.command, str)
        self.assertIsInstance(result.args, list)
        self.assertIsInstance(result.start_time, str)
        self.assertIsInstance(result.end_time, str)
        self.assertIsInstance(result.returncode, int)
        self.assertIsInstance(result.pid, int)
        self.assertIsInstance(result.duration_seconds, float)
        self.assertIsInstance(result.timeout_occurred, bool)
        self.assertIsInstance(result.killed, bool)
        self.assertIsInstance(result.success, bool)

        # Check result completion status
        if should_be_completed is not None:
            if should_be_completed:
                # CommandResult is always completed (no is_running field)
                if result.end_time is None or result.end_time == "":
                    error_msg = f"Command result was expected to be completed but has no end_time. "
                    error_msg += f"Command: '{result.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
                if result.returncode is None:
                    error_msg = f"Command result was expected to be completed but has no return_code. "
                    error_msg += f"Command: '{result.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
            else:
                # This is not applicable for CommandResult as it's always completed
                pass

        # Check result running status
        if should_be_running is not None:
            if should_be_running:
                # CommandResult is never running (always completed)
                error_msg = f"Command result was expected to be running but CommandResult is always completed. "
                error_msg += f"Command: '{result.command}'. "
                if message:
                    error_msg += f"Context: {message}"
                self.fail(error_msg)
            else:
                # CommandResult is always completed (not running)
                pass

    def assertCommandSuccess(self, response: CommandResponse, message: str = "") -> None:
        """Facade for assert_command_response focusing on success/failure."""
        self.assertCommandResponse(response, expected_success=True, message=message)

    def assertCommandFail(self, response: CommandResponse, message: str = "") -> None:
        """Facade for assert_command_response focusing on success/failure."""
        self.assertCommandResponse(response, expected_success=False, message=message)

    def assertResultCompleted(self, result: CommandResult) -> None:
        """Facade for assertCommandResult focusing on result completion."""
        self.assertCommandResult(result, should_be_completed=True)


__all__ = [
    "BaseSystemGatewayTest"
]
