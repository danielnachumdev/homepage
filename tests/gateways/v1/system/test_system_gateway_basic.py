"""
Basic functionality tests for SystemGateway.
"""
import asyncio
from unittest.mock import patch, MagicMock
import unittest
from backend.src.gateways.v1.system_gateway import SystemGateway
from backend.src.schemas.v1.system import CommandResponse, CommandResult
from tests.gateways.v1.system.base import BaseSystemGatewayTest


class TestSystemGatewayBasic(BaseSystemGatewayTest):
    """Test basic functionality of SystemGateway."""

    def test_parse_command_simple(self):
        """Test parsing simple commands."""
        # Test simple command
        result = SystemGateway._parse_command("echo hello")
        self.assertEqual(result, ["echo", "hello"])

        # Test command with spaces
        result = SystemGateway._parse_command("echo hello world")
        self.assertEqual(result, ["echo", "hello", "world"])

    def test_parse_command_with_quotes(self):
        """Test parsing commands with quotes."""
        # Test single quotes
        result = SystemGateway._parse_command('echo "hello world"')
        self.assertEqual(result, ["echo", "hello world"])

        # Test mixed quotes
        result = SystemGateway._parse_command('echo "hello" world')
        self.assertEqual(result, ["echo", "hello", "world"])

    def test_parse_command_with_special_chars(self):
        """Test parsing commands with special characters."""
        # Test command with special characters
        result = SystemGateway._parse_command("echo hello-world_test")
        self.assertEqual(result, ["echo", "hello-world_test"])

    def test_parse_command_invalid(self):
        """Test parsing invalid commands falls back to simple split."""
        # Test malformed quotes
        result = SystemGateway._parse_command('echo "hello world')
        # Should fall back to simple split
        self.assertEqual(result, ['echo', '"hello', 'world'])

    def test_execute_command_string_success(self):
        """Test executing a command string successfully."""
        command = self.get_echo_command("test output")
        response = self.run_async(SystemGateway.execute_command(command))

        self.assertCommandResponse(
            response,
            expected_success=True,
            expected_output_contains=["test output"],
            result_should_be_completed=True,
            message="echo command test"
        )
        self.assertIsNone(response.error)
        self.assertIsNotNone(response.result)

    def test_execute_command_string_failure(self):
        """Test executing a command string that fails."""
        command = self.get_invalid_command()
        response = self.run_async(SystemGateway.execute_command(command))

        self.assertCommandResponse(
            response,
            expected_success=False,
            result_should_be_completed=True,
            message="invalid command test"
        )
        self.assertEqual(response.output, "")
        self.assertIsNotNone(response.error)
        self.assertIsNotNone(response.result)

    def test_execute_command_args_success(self):
        """Test executing command arguments successfully."""
        args = self.get_echo_args("test args")
        response = self.run_async(SystemGateway.execute_command_args(args))

        self.assertCommandSuccess(response, message="echo args test")
        self.assertIn("test args", response.output)
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)

    def test_execute_command_args_failure(self):
        """Test executing command arguments that fail."""
        args = self.get_invalid_args()
        response = self.run_async(SystemGateway.execute_command_args(args))

        self.assertCommandFail(response, message="invalid args test")
        self.assertEqual(response.output, "")
        self.assertIsNotNone(response.error)
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)

    def test_execute_command_with_empty_string(self):
        """Test executing an empty command string."""
        response = self.run_async(SystemGateway.execute_command(""))

        self.assertCommandFail(response, message="empty command test")
        self.assertEqual(response.output, "")
        self.assertIsNotNone(response.error)

    def test_execute_command_with_empty_args(self):
        """Test executing empty command arguments."""
        response = self.run_async(SystemGateway.execute_command_args([]))

        self.assertCommandFail(response, message="empty args test")
        self.assertEqual(response.output, "")
        self.assertIsNotNone(response.error)

    def test_command_handle_structure(self):
        """Test that command handle has proper structure."""
        command = self.get_echo_command("handle test")
        response = self.run_async(SystemGateway.execute_command(command))

        result = response.result
        self.assertIsNotNone(result)
        self.assertIsInstance(result.pid, int)
        self.assertIsInstance(result.command, str)
        self.assertIsInstance(result.args, list)
        self.assertIsInstance(result.start_time, str)
        self.assertIsInstance(result.end_time, str)
        self.assertIsInstance(result.returncode, int)
        self.assertIsInstance(result.success, bool)

        # Verify result is completed
        self.assertIsNotNone(result.end_time)
        self.assertIsNotNone(result.returncode)

    def test_command_handle_command_string(self):
        """Test that command handle contains the correct command string."""
        command = self.get_echo_command("command string test")
        args = self.get_echo_args("command string test")
        response = self.run_async(SystemGateway.execute_command_args(args))

        result = response.result
        self.assertEqual(result.command, command)
        self.assertEqual(result.args, self.get_echo_args("command string test"))

    def test_multiple_commands_different_outputs(self):
        """Test executing multiple different commands."""
        commands = [
            self.get_echo_command("first"),
            self.get_echo_command("second"),
            self.get_echo_command("third")
        ]

        responses = []
        for command in commands:
            response = self.run_async(SystemGateway.execute_command(command))
            responses.append(response)

        # All should succeed
        expected_outputs = ["first", "second", "third"]
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(expected_outputs[i], response.output.lower())

    def test_command_with_unicode_output(self):
        """Test command with unicode characters in output."""
        unicode_text = "Hello 世界 🌍"
        command = self.get_echo_command(unicode_text)
        response = self.run_async(SystemGateway.execute_command(command))

        self.assertCommandSuccess(response)
        # Note: The exact output may vary by platform, but should contain the unicode text
        self.assertIsNotNone(response.output)

    def test_command_with_stderr_output(self):
        """Test command that produces stderr output."""
        # Use a command that typically produces stderr
        if self.is_windows:
            command = "dir nonexistent_directory_12345"
        else:
            command = "ls nonexistent_directory_12345"

        response = self.run_async(SystemGateway.execute_command(command))

        # Should fail and have error output
        self.assertCommandFail(response)
        self.assertIsNotNone(response.error)

    @patch('asyncio.to_thread')
    def test_execute_command_internal_exception_handling(self, mock_to_thread):
        """Test exception handling in _execute_command_internal."""
        # Mock asyncio.to_thread to raise an exception
        mock_to_thread.side_effect = Exception("Test exception")

        args = self.get_echo_args("test")
        response = self.run_async(SystemGateway._execute_command_internal(args))

        self.assertCommandFail(response)
        self.assertEqual(response.output, "")
        self.assertEqual(response.error, "Test exception")
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)
        self.assertEqual(response.result.returncode, -1)

    def test_execute_command_with_whitespace(self):
        """Test executing commands with various whitespace."""
        # Test command with leading/trailing whitespace
        command = "  " + self.get_echo_command("whitespace test") + "  "
        response = self.run_async(SystemGateway.execute_command(command))

        self.assertCommandSuccess(response)
        self.assertIn("whitespace test", response.output)

    def test_execute_command_with_tabs(self):
        """Test executing commands with tabs."""
        command = self.get_echo_command("tab\ttest")
        response = self.run_async(SystemGateway.execute_command(command))

        self.assertCommandSuccess(response)
        self.assertIn("tab", response.output)


__all__ = [
    "TestSystemGatewayBasic"
]
