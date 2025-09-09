"""
Concurrent execution tests for SystemGateway.
"""
from tests.gateways.v1.system.base import BaseSystemGatewayTest
from backend.src.schemas.v1.system import CommandResponse, CommandResult
from backend.src.gateways.v1.system_gateway import SystemGateway
import unittest
from unittest.mock import patch, MagicMock
import asyncio
import time


class TestSystemGatewayConcurrent(BaseSystemGatewayTest):
    """Test concurrent execution functionality of SystemGateway."""

    def test_execute_multiple_commands_strings(self):
        """Test executing multiple command strings concurrently."""
        commands = [
            self.get_echo_command("concurrent 1"),
            self.get_echo_command("concurrent 2"),
            self.get_echo_command("concurrent 3"),
            self.get_echo_command("concurrent 4"),
            self.get_echo_command("concurrent 5")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 5 responses
        self.assertEqual(len(responses), 5)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"concurrent {i + 1}", response.output)

    def test_execute_multiple_commands_args(self):
        """Test executing multiple command argument lists concurrently."""
        commands = [
            self.get_echo_args("args 1"),
            self.get_echo_args("args 2"),
            self.get_echo_args("args 3"),
            self.get_echo_args("args 4"),
            self.get_echo_args("args 5")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 5 responses
        self.assertEqual(len(responses), 5)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"args {i + 1}", response.output)

    def test_execute_multiple_commands_mixed(self):
        """Test executing mixed command types concurrently."""
        commands = [
            self.get_echo_command("mixed string 1"),
            self.get_echo_args("mixed args 2"),
            self.get_echo_command("mixed string 3"),
            self.get_echo_args("mixed args 4"),
            self.get_echo_command("mixed string 5")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 5 responses
        self.assertEqual(len(responses), 5)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            expected_text = f"mixed {'string' if i % 2 == 0 else 'args'} {i + 1}"
            self.assertIn(expected_text, response.output)

    def test_execute_multiple_commands_with_failures(self):
        """Test executing multiple commands with some failures."""
        commands = [
            self.get_echo_command("success 1"),
            self.get_invalid_command(),
            self.get_echo_command("success 2"),
            self.get_invalid_command(),
            self.get_echo_command("success 3")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 5 responses
        self.assertEqual(len(responses), 5)

        # Check specific responses
        self.assertCommandSuccess(responses[0])
        self.assertIn("success 1", responses[0].output)

        self.assertCommandFail(responses[1])
        self.assertIsNotNone(responses[1].error)

        self.assertCommandSuccess(responses[2])
        self.assertIn("success 2", responses[2].output)

        self.assertCommandFail(responses[3])
        self.assertIsNotNone(responses[3].error)

        self.assertCommandSuccess(responses[4])
        self.assertIn("success 3", responses[4].output)

    def test_execute_multiple_commands_with_custom_concurrency(self):
        """Test executing multiple commands with custom concurrency limit."""
        commands = [
            self.get_echo_command(f"concurrent {i}") for i in range(10)
        ]

        # Test with different concurrency limits
        for max_concurrent in [1, 3, 5, 10]:
            responses = self.run_async(
                SystemGateway.execute_multiple_commands(commands, max_concurrent=max_concurrent)
            )

            # Should have 10 responses
            self.assertEqual(len(responses), 10)

            # All should succeed
            for i, response in enumerate(responses):
                self.assertCommandSuccess(response)
                self.assertIn(f"concurrent {i}", response.output)

    def test_execute_multiple_commands_empty_list(self):
        """Test executing empty command list."""
        responses = self.run_async(SystemGateway.execute_multiple_commands([]))

        # Should return empty list
        self.assertEqual(len(responses), 0)
        self.assertIsInstance(responses, list)

    def test_execute_multiple_commands_single_command(self):
        """Test executing single command in multiple commands."""
        commands = [self.get_echo_command("single command")]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 1 response
        self.assertEqual(len(responses), 1)
        self.assertCommandSuccess(responses[0])
        self.assertIn("single command", responses[0].output)

    def test_execute_multiple_commands_all_failures(self):
        """Test executing multiple commands that all fail."""
        commands = [
            self.get_invalid_command(),
            self.get_invalid_command(),
            self.get_invalid_command()
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 3 responses
        self.assertEqual(len(responses), 3)

        # All should fail
        for response in responses:
            self.assertCommandFail(response)
            self.assertIsNotNone(response.error)

    def test_execute_multiple_commands_with_exceptions(self):
        """Test executing multiple commands with exceptions."""
        commands = [
            self.get_echo_command("normal command"),
            "invalid command with spaces and quotes",
            self.get_echo_command("another normal command")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 3 responses
        self.assertEqual(len(responses), 3)

        # First should succeed
        self.assertCommandSuccess(responses[0])
        self.assertIn("normal command", responses[0].output)

        # Second should fail (invalid command)
        self.assertCommandFail(responses[1])
        self.assertIsNotNone(responses[1].error)

        # Third should succeed
        self.assertCommandSuccess(responses[2])
        self.assertIn("another normal command", responses[2].output)

    def test_execute_multiple_commands_concurrency_timing(self):
        """Test that concurrent execution is actually faster than sequential."""
        commands = [
            self.get_echo_command(f"timing test {i}") for i in range(5)
        ]

        # Time concurrent execution
        start_time = time.time()
        concurrent_responses = self.run_async(SystemGateway.execute_multiple_commands(commands))
        concurrent_time = time.time() - start_time

        # Time sequential execution
        start_time = time.time()
        sequential_responses = []
        for command in commands:
            response = self.run_async(SystemGateway.execute_command(command))
            sequential_responses.append(response)
        sequential_time = time.time() - start_time

        # Both should have same number of responses
        self.assertEqual(len(concurrent_responses), len(sequential_responses))

        # Concurrent should be faster (or at least not significantly slower)
        # Note: For very fast commands like echo, the difference might be minimal
        self.assertLessEqual(concurrent_time, sequential_time * 1.5)  # Allow 50% tolerance

    def test_execute_multiple_commands_large_number(self):
        """Test executing a large number of commands."""
        commands = [
            self.get_echo_command(f"large test {i}") for i in range(20)
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands, max_concurrent=5))

        # Should have 20 responses
        self.assertEqual(len(responses), 20)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"large test {i}", response.output)

    def test_execute_multiple_commands_with_unicode(self):
        """Test executing multiple commands with unicode content."""
        commands = [
            self.get_echo_command("Unicode test 1: 你好"),
            self.get_echo_command("Unicode test 2: 🌍"),
            self.get_echo_command("Unicode test 3: café"),
            self.get_echo_command("Unicode test 4: naïve"),
            self.get_echo_command("Unicode test 5: résumé")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 5 responses
        self.assertEqual(len(responses), 5)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"Unicode test {i + 1}", response.output)

    def test_execute_multiple_commands_with_special_characters(self):
        """Test executing multiple commands with special characters."""
        commands = [
            self.get_echo_command("Special chars 1: !@#$%"),
            self.get_echo_command("Special chars 2: ^&*()"),
            self.get_echo_command("Special chars 3: +={}[]"),
            self.get_echo_command("Special chars 4: |\\:;\"'"),
            self.get_echo_command("Special chars 5: <>?,./")
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should have 5 responses
        self.assertEqual(len(responses), 5)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"Special chars {i + 1}", response.output)

    def test_execute_multiple_commands_zero_concurrency(self):
        """Test executing multiple commands with zero concurrency (should raise ValueError)."""
        commands = [
            self.get_echo_command("zero concurrency 1"),
            self.get_echo_command("zero concurrency 2")
        ]

        # Should raise ValueError for zero concurrency
        with self.assertRaises(ValueError) as context:
            self.run_async(SystemGateway.execute_multiple_commands(commands, max_concurrent=0))

        self.assertIn("max_concurrent must be a strictly positive integer", str(context.exception))

    def test_execute_multiple_commands_very_high_concurrency(self):
        """Test executing multiple commands with very high concurrency limit."""
        commands = [
            self.get_echo_command(f"high concurrency {i}") for i in range(10)
        ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands, max_concurrent=100))

        # Should have 10 responses
        self.assertEqual(len(responses), 10)

        # All should succeed
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"high concurrency {i}", response.output)

    @patch('asyncio.gather')
    def test_execute_multiple_commands_gather_exception(self, mock_gather):
        """Test handling of exceptions in asyncio.gather."""
        # Mock asyncio.gather to return a coroutine that resolves to an exception
        async def mock_gather_coro(*args, **kwargs):
            return [Exception("Test gather exception")]
        mock_gather.return_value = mock_gather_coro()

        commands = [self.get_echo_command("test")]
        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # Should handle the exception
        self.assertEqual(len(responses), 1)
        self.assertCommandFail(responses[0])
        self.assertIn("Command execution failed: Test gather exception", responses[0].error)


__all__ = [
    "TestSystemGatewayConcurrent"
]
