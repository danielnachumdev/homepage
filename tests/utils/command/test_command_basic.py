"""
Test basic AsyncCommand functionality.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import AsyncCommand, CommandType, CommandState


class TestCommandBasic(BaseCommandTest):
    """Test basic AsyncCommand functionality."""

    def test_command_initialization(self) -> None:
        """Test command initialization with various parameters."""
        # Basic initialization
        cmd: AsyncCommand = self.create_simple_command(['echo', 'test'])
        self.assertEqual(cmd.args, ['echo', 'test'])
        self.assertTrue(cmd.blocking)
        self.assertEqual(cmd.command_type, CommandType.CLI)
        self.assertIsNone(cmd.cwd)
        self.assertEqual(cmd.env, {})
        self.assertIsNone(cmd.timeout)
        self.assertEqual(cmd.state, CommandState.PENDING)

    def test_command_initialization_with_parameters(self) -> None:
        """Test command initialization with custom parameters."""
        cwd: Path = Path("/tmp")
        env: Dict[str, str] = {"TEST_VAR": "test_value"}
        timeout: float = 30.0

        cmd: AsyncCommand = AsyncCommand(
            args=['python', '--version'],
            command_type=CommandType.CLI,
            cwd=cwd,
            env=env,
            timeout=timeout
        )

        self.assertEqual(cmd.args, ['python', '--version'])
        self.assertEqual(cmd.command_type, CommandType.CLI)
        self.assertEqual(cmd.cwd, cwd)
        self.assertEqual(cmd.env, env)
        self.assertEqual(cmd.timeout, timeout)
        self.assertEqual(cmd.state, CommandState.PENDING)

    def test_command_properties(self) -> None:
        """Test command property access."""
        cmd: AsyncCommand = self.create_simple_command(['echo', 'test'])

        # Initial state
        self.assertEqual(cmd.state, CommandState.PENDING)
        self.assertFalse(cmd.is_running)
        self.assertFalse(cmd.is_completed)
        self.assertIsNone(cmd.result)

    def test_command_factory_methods(self) -> None:
        """Test command factory methods."""
        # Shell command
        shell_cmd: AsyncCommand = AsyncCommand.shell("echo 'Hello World'")
        self.assertEqual(shell_cmd.args, ["echo 'Hello World'"])
        self.assertEqual(shell_cmd.command_type, CommandType.CLI)

    def test_simple_command_execution(self) -> None:
        """Test simple command execution."""
        cmd: AsyncCommand = self.create_successful_command()
        result = self.run_async(self.execute_command(cmd))

        self.assert_command_success(result, "Hello World")
        self.assertEqual(cmd.state, CommandState.COMPLETED)
        self.assertTrue(cmd.is_completed)

    def test_command_execution_with_cwd(self) -> None:
        """Test command execution with working directory."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            cmd: AsyncCommand = AsyncCommand(
                args=['echo', 'test'],
                cwd=temp_dir
            )
            result = self.run_async(self.execute_command(cmd))

            self.assert_command_success(result, "test")

    def test_command_execution_with_env(self) -> None:
        """Test command execution with environment variables."""
        cmd: AsyncCommand = AsyncCommand(
            args=['cmd', '/c', 'echo', '%TEST_VAR%'],
            env={"TEST_VAR": "test_value"}
        )
        result = self.run_async(self.execute_command(cmd))

        self.assert_command_success(result, "test_value")

    def test_command_execution_failure(self) -> None:
        """Test command execution failure."""
        cmd: AsyncCommand = self.create_failing_command()
        result = self.run_async(self.execute_command(cmd))

        self.assert_command_failure(result)

    def test_command_string_representation(self) -> None:
        """Test command string representation."""
        cmd: AsyncCommand = self.create_simple_command(['echo', 'test'])
        repr_str: str = repr(cmd)
        self.assertIn("AsyncCommand", repr_str)
        self.assertIn("['echo', 'test']", repr_str)
        self.assertIn("pending", repr_str)

    def test_command_callback_execution(self) -> None:
        """Test command callback execution."""
        start_called: bool = False
        complete_called: bool = False
        error_called: bool = False

        def on_start(command: AsyncCommand) -> None:
            nonlocal start_called
            start_called = True

        def on_complete(command: AsyncCommand, result: Any) -> None:
            nonlocal complete_called
            complete_called = True

        def on_error(command: AsyncCommand, error: Exception) -> None:
            nonlocal error_called
            error_called = True

        cmd: AsyncCommand = AsyncCommand(
            args=['echo', 'test'],
            on_start=on_start,
            on_complete=on_complete,
            on_error=on_error
        )

        result = self.run_async(self.execute_command(cmd))

        self.assertTrue(start_called)
        self.assertTrue(complete_called)
        self.assertFalse(error_called)
        self.assert_command_success(result)

    def test_command_error_callback(self) -> None:
        """Test command error callback execution."""
        error_called: bool = False

        def on_error(command: AsyncCommand, error: Exception) -> None:
            nonlocal error_called
            error_called = True

        cmd: AsyncCommand = AsyncCommand(
            args=['nonexistent_command_12345'],
            on_error=on_error
        )

        result = self.run_async(self.execute_command(cmd))

        self.assertTrue(error_called)
        self.assert_command_failure(result)


__all__ = [
    "TestCommandBasic"
]
