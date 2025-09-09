"""
Test Command integration scenarios.
"""

import tempfile
from pathlib import Path
from typing import List, Dict

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import Command, CommandExecutionResult


class TestCommandIntegration(BaseCommandTest):
    """Test Command integration scenarios."""

    def test_multiple_commands_sequential(self) -> None:
        """Test executing multiple commands sequentially."""
        commands: List[Command] = [
            self.create_simple_command(['echo', 'First']),
            self.create_simple_command(['echo', 'Second']),
            self.create_simple_command(['echo', 'Third'])
        ]

        results: List[CommandExecutionResult] = []
        for cmd in commands:
            result: CommandExecutionResult = self.run_async(cmd.execute())
            results.append(result)

        # All commands should succeed
        for result in results:
            self.assert_command_success(result)

    def test_command_with_working_directory(self) -> None:
        """Test command execution with working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file: Path = Path(temp_dir) / 'test.txt'
            test_file.write_text('Hello World')

            # Run command in the temp directory
            cmd: Command = self.create_simple_command(
                ['type', 'test.txt'],
                cwd=temp_dir
            )
            result: CommandExecutionResult = self.run_async(cmd.execute())

            self.assert_command_success(result, 'Hello World')

    def test_command_environment_variables(self) -> None:
        """Test command execution with environment variables."""
        env: Dict[str, str] = {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2'
        }

        cmd: Command = self.create_simple_command(
            ['cmd', '/c', 'echo', '%TEST_VAR1%', '%TEST_VAR2%'],
            env=env
        )
        result: CommandExecutionResult = self.run_async(cmd.execute())

        self.assert_command_success(result)
        self.assertIn('value1', result.stdout)
        self.assertIn('value2', result.stdout)
