"""
Test async command execution.
"""

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import AsyncCommand, CommandState, CommandExecutionResult


class TestCommandAsync(BaseCommandTest):
    """Test async command execution."""

    def test_async_command_execution(self) -> None:
        """Test async command execution."""
        cmd: AsyncCommand = self.create_simple_command(['echo', 'Hello Async'])
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assertEqual(result.state, CommandState.COMPLETED)
        self.assertTrue(result.success)
        self.assertIn('Hello Async', result.stdout)
        self.assert_command_success(result, 'Hello Async')

    def test_async_command_execution_with_timeout(self) -> None:
        """Test async command execution with timeout."""
        # Use a command that will actually timeout
        cmd: AsyncCommand = AsyncCommand(
            args=['cmd', '/c', 'ping', '127.0.0.1', '-n', '1000'],  # Long running command
            timeout=0.1  # Very short timeout
        )
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assertEqual(result.state, CommandState.TIMEOUT)
        self.assertFalse(result.success)
        self.assertTrue(result.timeout_occurred)
        self.assert_command_timeout(result)
