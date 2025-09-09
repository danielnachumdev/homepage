"""
Test command execution functionality.
"""

import tempfile
from typing import Dict, Any, Optional, Callable
from unittest.mock import patch

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import Command, CommandType, CommandState, CommandExecutionResult


class TestCommandExecution(BaseCommandTest):
    """Test command execution functionality."""

    def test_cli_command_execution_success(self) -> None:
        """Test successful CLI command execution."""
        cmd: Command = self.create_successful_command()
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_success(result, 'Hello World')
        self.assertEqual(result.command_type, CommandType.CLI)

    def test_cli_command_execution_failure(self) -> None:
        """Test failed CLI command execution."""
        cmd: Command = self.create_failing_command()
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_failure(result, 'failed to start')

    def test_gui_command_execution(self) -> None:
        """Test GUI command execution."""
        cmd: Command = self.create_gui_command()
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_success(result)
        self.assertEqual(result.command_type, CommandType.GUI)

    def test_command_execution_with_timeout(self) -> None:
        """Test command execution with timeout."""
        cmd: Command = self.create_timeout_command(timeout=1.0)
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_timeout(result)

    def test_command_execution_with_cwd(self) -> None:
        """Test command execution with working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd: Command = self.create_simple_command(
                ['cmd', '/c', 'echo', '%CD%'],
                cwd=temp_dir
            )
            result: CommandExecutionResult = self.run_async(cmd.execute())

            self.assert_command_success(result)
            # The output should contain the temp directory path
            self.assertIn(temp_dir.replace('\\', '/'), result.stdout.replace('\\', '/'))

    def test_command_execution_with_env(self) -> None:
        """Test command execution with environment variables."""
        env: Dict[str, str] = {'TEST_VAR': 'test_value'}
        cmd: Command = self.create_simple_command(
            ['cmd', '/c', 'echo', '%TEST_VAR%'],
            env=env
        )
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_success(result)
        self.assertIn('test_value', result.stdout)

    def test_command_execution_callbacks(self) -> None:
        """Test command execution with callbacks."""
        start_called: bool = False
        complete_called: bool = False
        error_called: bool = False

        def on_start(command: Command) -> None:
            nonlocal start_called
            start_called = True

        def on_complete(command: Command, result: CommandExecutionResult) -> None:
            nonlocal complete_called
            complete_called = True

        def on_error(command: Command, exception: Exception) -> None:
            nonlocal error_called
            error_called = True

        cmd: Command = self.create_simple_command(
            ['echo', 'test'],
            on_start=on_start,
            on_complete=on_complete,
            on_error=on_error
        )

        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assertTrue(start_called)
        self.assertTrue(complete_called)
        self.assertFalse(error_called)
        self.assert_command_success(result)

    def test_command_execution_error_callback(self) -> None:
        """Test command execution error callback."""
        error_called: bool = False
        captured_exception: Optional[Exception] = None

        def on_error(command: Command, exception: Exception) -> None:
            nonlocal error_called, captured_exception
            error_called = True
            captured_exception = exception

        cmd: Command = self.create_failing_command(on_error=on_error)
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assertTrue(error_called)
        self.assertIsNotNone(captured_exception)
        self.assert_command_failure(result)
