"""
Test CommandExecutionResult functionality.
"""

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import Command, CommandExecutionResult


class TestCommandResult(BaseCommandTest):
    """Test CommandExecutionResult functionality."""

    def test_command_result_properties(self) -> None:
        """Test CommandExecutionResult properties."""
        cmd: Command = self.create_simple_command(['echo', 'test'])
        result: CommandExecutionResult = self.run_async(cmd.execute())

        # Test properties
        self.assertTrue(result.success)
        self.assertIn('test', result.stdout)
        self.assertEqual(result.command, cmd)

    def test_command_result_conversion(self) -> None:
        """Test CommandExecutionResult properties."""
        cmd: Command = self.create_simple_command(['echo', 'test'])
        result: CommandExecutionResult = self.run_async(cmd.execute())

        # Test basic properties
        self.assertTrue(result.success)
        self.assertEqual(result.return_code, 0)
        self.assertIn('test', result.stdout)
        self.assertIsNotNone(result.pid)
        self.assertGreater(result.execution_time, 0)

    def test_command_result_string_representation(self) -> None:
        """Test CommandExecutionResult string representation."""
        cmd: Command = self.create_simple_command(['echo', 'test'])
        result: CommandExecutionResult = self.run_async(cmd.execute())

        str_repr: str = str(result)
        self.assertIn('SUCCESS', str_repr)
        self.assertIn('0', str_repr)  # return code
