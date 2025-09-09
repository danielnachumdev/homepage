"""
Timeout handling tests for SystemGateway.
"""
from tests.gateways.v1.system.base import BaseSystemGatewayTest
from backend.src.gateways.v1.system_gateway import SystemGateway
from unittest.mock import patch
import asyncio


class TestSystemGatewayTimeout(BaseSystemGatewayTest):
    """Test timeout functionality of SystemGateway."""

    def test_execute_command_with_timeout_success(self):
        """Test executing a command with timeout that completes in time."""
        command = self.get_echo_command("timeout test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=5.0))

        self.assertCommandSuccess(response)
        self.assertIn("timeout test", response.output)
        self.assertIsNone(response.error)
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)

    def test_execute_command_with_timeout_failure(self):
        """Test executing a command with timeout that fails."""
        command = self.get_invalid_command()
        response = self.run_async(SystemGateway.execute_command(command, timeout=5.0))

        self.assertCommandFail(response)
        self.assertEqual(response.output, "")
        self.assertIsNotNone(response.error)
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)

    def test_execute_command_args_with_timeout_success(self):
        """Test executing command args with timeout that completes in time."""
        args = self.get_echo_args("timeout args test")
        response = self.run_async(SystemGateway.execute_command_args(args, timeout=5.0))

        self.assertCommandSuccess(response)
        self.assertIn("timeout args test", response.output)
        self.assertIsNone(response.error)
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)

    def test_execute_command_args_with_timeout_failure(self):
        """Test executing command args with timeout that fails."""
        args = self.get_invalid_args()
        response = self.run_async(SystemGateway.execute_command_args(args, timeout=5.0))

        self.assertCommandFail(response)
        self.assertEqual(response.output, "")
        self.assertIsNotNone(response.error)
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)

    def test_execute_command_with_short_timeout(self):
        """Test executing a command with a very short timeout."""
        command = self.get_echo_command("short timeout test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=0.1))

        # Should still succeed as echo is very fast
        self.assertCommandSuccess(response)
        self.assertIn("short timeout test", response.output)

    def test_execute_command_with_long_timeout(self):
        """Test executing a command with a long timeout."""
        command = self.get_echo_command("long timeout test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=30.0))

        self.assertCommandSuccess(response)
        self.assertIn("long timeout test", response.output)

    def test_execute_command_with_zero_timeout(self):
        """Test executing a command with zero timeout."""
        command = self.get_echo_command("zero timeout test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=0.0))

        # Should still succeed as echo is very fast
        self.assertCommandSuccess(response)
        self.assertIn("zero timeout test", response.output)

    def test_execute_command_with_negative_timeout(self):
        """Test executing a command with negative timeout."""
        command = self.get_echo_command("negative timeout test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=-1.0))

        # Should still succeed as echo is very fast
        self.assertCommandSuccess(response)
        self.assertIn("negative timeout test", response.output)

    def test_execute_command_with_none_timeout(self):
        """Test executing a command with None timeout (should work like no timeout)."""
        command = self.get_echo_command("none timeout test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=None))

        self.assertCommandSuccess(response)
        self.assertIn("none timeout test", response.output)

    @patch('asyncio.wait_for')
    def test_execute_command_timeout_exception(self, mock_wait_for):
        """Test timeout exception handling."""
        # Mock asyncio.wait_for to raise TimeoutError
        mock_wait_for.side_effect = asyncio.TimeoutError()

        args = self.get_echo_args("timeout exception test")
        response = self.run_async(SystemGateway.execute_command_args(args, timeout=1.0))

        self.assertCommandFail(response)
        self.assertEqual(response.output, "")
        self.assertEqual(response.error, "Command timed out after 1.0 seconds")
        self.assertIsNotNone(response.result)
        self.assertResultCompleted(response.result)
        self.assertEqual(response.result.returncode, -1)

    def test_timeout_handle_structure(self):
        """Test that timeout creates proper handle structure."""
        command = self.get_echo_command("timeout handle test")
        response = self.run_async(SystemGateway.execute_command(command, timeout=5.0))

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

    def test_timeout_vs_no_timeout_consistency(self):
        """Test that timeout and no-timeout versions produce consistent results."""
        command = self.get_echo_command("consistency test")

        # Execute with timeout
        response_with_timeout = self.run_async(SystemGateway.execute_command(command, timeout=5.0))

        # Execute without timeout
        response_without_timeout = self.run_async(SystemGateway.execute_command(command))

        # Both should succeed and have similar output
        self.assertCommandSuccess(response_with_timeout)
        self.assertCommandSuccess(response_without_timeout)

        # Output should be similar (may have slight differences due to timing)
        self.assertIn("consistency test", response_with_timeout.output)
        self.assertIn("consistency test", response_without_timeout.output)

    def test_timeout_with_different_commands(self):
        """Test timeout with different types of commands."""
        commands = [
            self.get_echo_command("command 1"),
            self.get_echo_command("command 2"),
            self.get_echo_command("command 3")
        ]

        for i, command in enumerate(commands):
            response = self.run_async(SystemGateway.execute_command(command, timeout=2.0))

            self.assertCommandSuccess(response)
            self.assertIn(f"command {i + 1}", response.output)
            self.assertIsNone(response.error)

    def test_timeout_with_failing_commands(self):
        """Test timeout with commands that fail."""
        commands = [
            self.get_invalid_command(),
            "another_invalid_command_12345",
            "yet_another_invalid_command_67890"
        ]

        for command in commands:
            response = self.run_async(SystemGateway.execute_command(command, timeout=2.0))

            self.assertCommandFail(response)
            self.assertEqual(response.output, "")
            self.assertIsNotNone(response.error)

    def test_timeout_edge_cases(self):
        """Test timeout with edge case values."""
        command = self.get_echo_command("edge case test")

        # Test very small timeout
        response = self.run_async(SystemGateway.execute_command(command, timeout=0.001))
        self.assertCommandSuccess(response)

        # Test very large timeout
        response = self.run_async(SystemGateway.execute_command(command, timeout=3600.0))
        self.assertCommandSuccess(response)

    def test_timeout_with_unicode_commands(self):
        """Test timeout with unicode commands."""
        unicode_command = self.get_echo_command("Unicode test: 你好世界 🌍")
        response = self.run_async(SystemGateway.execute_command(unicode_command, timeout=5.0))

        self.assertCommandSuccess(response)
        self.assertIsNotNone(response.output)

    def test_timeout_with_special_characters(self):
        """Test timeout with special characters in commands."""
        special_command = self.get_echo_command("Special chars: !@#$%^&*()")
        response = self.run_async(SystemGateway.execute_command(special_command, timeout=5.0))

        self.assertCommandSuccess(response)
        self.assertIsNotNone(response.output)


__all__ = [
    "TestSystemGatewayTimeout"
]
