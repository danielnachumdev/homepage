"""
Test command error handling.
"""

from unittest.mock import patch, MagicMock
from typing import Any

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import Command, CommandExecutionResult


class TestCommandErrorHandling(BaseCommandTest):
    """Test command error handling."""

    def test_command_execution_exception_handling(self) -> None:
        """Test handling of execution exceptions."""
        with self.mock_subprocess_failure("Test error"):
            cmd: Command = self.create_simple_command(['test'])
            result: CommandExecutionResult = self.run_async(cmd.execute())

            self.assert_command_failure(result, 'test error')

    def test_command_timeout_handling(self) -> None:
        """Test command timeout handling."""
        cmd: Command = self.create_timeout_command(timeout=0.1)
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_timeout(result)
