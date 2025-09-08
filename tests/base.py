"""
Common base test classes for all tests.
"""
import asyncio
import unittest
from typing import Any, Dict, List, Optional, Union, TypeVar, Awaitable, Coroutine

# Import the actual response types
from backend.src.schemas.v1.system import CommandResponse, CommandHandle

# Type variable for generic return types
T = TypeVar('T')


class BaseTest(unittest.TestCase):
    """Base test class with common functionality for all tests."""

    def _setup_test_logger(self):
        """Set up a unique logger for this test method."""
        test_class_name = self.__class__.__name__
        test_method_name = getattr(self, '_testMethodName', 'unknown_test')
        logger_name = f"{test_class_name}.{test_method_name}"

        import logging
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        # Add a handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Set up unique logger for this test method
        self._setup_test_logger()

    def tearDown(self):
        """Clean up after each test method."""
        self.loop.close()

    def run_async(self, coro: Union[Coroutine[Any, Any, T], Awaitable[T]]) -> T:
        """Run an async coroutine in the test loop and return the result with proper typing."""
        return self.loop.run_until_complete(coro)

    def assertCommandResponse(self, response: CommandResponse,
                              expected_success: Optional[bool] = None,
                              expected_output_contains: Optional[List[str]] = None,
                              expected_error_contains: Optional[List[str]] = None,
                              handle_should_be_completed: Optional[bool] = None,
                              handle_should_be_running: Optional[bool] = None,
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

        # Check handle validation
        if response.handle:
            self.assertCommandHandle(
                response.handle,
                should_be_completed=handle_should_be_completed,
                should_be_running=handle_should_be_running,
                message=message
            )

    def assertCommandHandle(self, handle: CommandHandle,
                            should_be_completed: Optional[bool] = None,
                            should_be_running: Optional[bool] = None,
                            message: str = "") -> None:
        """Comprehensive assertion method for command handles with detailed error logging."""

        # Validate handle structure
        self.assertIsInstance(handle, CommandHandle)
        self.assertIsInstance(handle.command, str)
        self.assertIsInstance(handle.args, list)
        self.assertIsInstance(handle.start_time, str)
        self.assertIsInstance(handle.is_running, bool)

        if handle.end_time is not None:
            self.assertIsInstance(handle.end_time, str)
        if handle.return_code is not None:
            self.assertIsInstance(handle.return_code, int)

        # Check handle completion status
        if should_be_completed is not None:
            if should_be_completed:
                if handle.is_running:
                    error_msg = f"Command handle was expected to be completed but is still running. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
                if handle.end_time is None:
                    error_msg = f"Command handle was expected to be completed but has no end_time. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
                if handle.return_code is None:
                    error_msg = f"Command handle was expected to be completed but has no return_code. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
            else:
                if not handle.is_running:
                    error_msg = f"Command handle was expected to be running but is completed. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)

        # Check handle running status
        if should_be_running is not None:
            if should_be_running:
                if not handle.is_running:
                    error_msg = f"Command handle was expected to be running but is completed. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
                if handle.end_time is not None:
                    error_msg = f"Command handle was expected to be running but has end_time. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
                if handle.return_code is not None:
                    error_msg = f"Command handle was expected to be running but has return_code. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)
            else:
                if handle.is_running:
                    error_msg = f"Command handle was expected to be completed but is still running. "
                    error_msg += f"Command: '{handle.command}'. "
                    if message:
                        error_msg += f"Context: {message}"
                    self.fail(error_msg)

    def assertCommandSuccess(self, response: CommandResponse, message: str = "") -> None:
        """Facade for assert_command_response focusing on success/failure."""
        self.assertCommandResponse(response, expected_success=True, message=message)

    def assertCommandFail(self, response: CommandResponse, message: str = "") -> None:
        """Facade for assert_command_response focusing on success/failure."""
        self.assertCommandResponse(response, expected_success=False, message=message)

    def assertHandleCompleted(self, handle: CommandHandle) -> None:
        """Facade for assertCommandHandle focusing on handle completion."""
        self.assertCommandHandle(handle, should_be_completed=True)


__all__ = [
    "BaseTest"
]
