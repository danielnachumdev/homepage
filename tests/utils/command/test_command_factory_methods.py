"""
Test Command factory methods.
"""

import tempfile
from pathlib import Path

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import Command, CommandType, CommandExecutionResult


class TestCommandFactoryMethods(BaseCommandTest):
    """Test Command factory methods."""

    def test_shell_command_factory(self) -> None:
        """Test shell command factory method."""
        cmd: Command = Command.shell('echo Hello World')

        self.assertEqual(cmd.args, ['echo Hello World'])
        self.assertEqual(cmd.command_type, CommandType.CLI)
        self.assertTrue(cmd.blocking)

        result: CommandExecutionResult = self.run_async(cmd.execute())
        self.assert_command_success(result, 'Hello World')

    def test_shell_command_factory_with_parameters(self) -> None:
        """Test shell command factory with additional parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd: Command = Command.shell(
                'echo %CD%',
                cwd=temp_dir,
                timeout=10.0
            )

            self.assertEqual(cmd.cwd, Path(temp_dir))
            self.assertEqual(cmd.timeout, 10.0)

            result: CommandExecutionResult = self.run_async(cmd.execute())
            self.assert_command_success(result)
