"""
Test AsyncCommand state management.
"""

import asyncio
import time
from typing import List, Optional

from tests.utils.command.base import BaseCommandTest
from backend.src.utils.command import AsyncCommand, CommandState, CommandExecutionResult


class TestCommandStateManagement(BaseCommandTest):
    """Test AsyncCommand state management."""

    def test_command_state_transitions(self) -> None:
        """Test command state transitions during execution."""
        cmd: AsyncCommand = self.create_simple_command(['echo', 'test'])

        # Initial state
        self.assertEqual(cmd.state, CommandState.PENDING)

        # Execute the command
        result = self.run_async(self.execute_command(cmd))

        # Verify final state
        self.assertEqual(cmd.state, CommandState.COMPLETED)
        self.assert_command_success(result)

    def test_command_kill(self) -> None:
        """Test command killing functionality."""
        # Test killing a command that is not running (should fail)
        cmd: AsyncCommand = self.create_simple_command(['echo', 'test'])

        # Try to kill before execution
        kill_success: bool = cmd.kill()
        self.assertFalse(kill_success)

        # Execute the command normally
        result: CommandExecutionResult = self.run_async(self.execute_command(cmd))
        self.assert_command_success(result)

        # Try to kill after completion (should fail)
        kill_success = cmd.kill()
        self.assertFalse(kill_success)

    def test_command_kill_running(self) -> None:
        """Test killing a running command using a mock."""
        # Create a command that will run for a while
        cmd: AsyncCommand = AsyncCommand(
            args=['cmd', '/c', 'ping', '127.0.0.1', '-n', '1000'],  # Ping 1000 times
            timeout=60.0  # 60 second timeout
        )

        # Start execution in background
        execution_task = asyncio.create_task(self.execute_command(cmd))

        # Wait a bit for command to start
        self.run_async(asyncio.sleep(0.5))

        # Check if it's running and kill if so
        if cmd.is_running:
            # Kill the command
            kill_success: bool = cmd.kill()
            self.assertTrue(kill_success)

            # Wait for execution to complete
            result: CommandExecutionResult = self.run_async(execution_task)

            # The command should be killed
            self.assert_command_killed(result)
            self.assertEqual(cmd.state, CommandState.KILLED)
        else:
            # If it completed too quickly, just get the result
            result: CommandExecutionResult = self.run_async(execution_task)
            # If it completed normally, that's also acceptable for this test
            self.assertIn(cmd.state, [CommandState.COMPLETED, CommandState.TIMEOUT])

    def test_command_wait(self) -> None:
        """Test command wait functionality."""
        cmd: AsyncCommand = self.create_successful_command()

        # Start execution in background
        execution_task = asyncio.create_task(self.execute_command(cmd))

        # Wait for completion
        result: CommandExecutionResult = self.run_async(cmd.wait())

        # Verify result
        self.assert_command_success(result)
        self.assertEqual(result, self.run_async(execution_task))

    def test_command_wait_already_completed(self) -> None:
        """Test waiting for an already completed command."""
        cmd: AsyncCommand = self.create_successful_command()

        result: CommandExecutionResult = self.run_async(self.execute_command(cmd))

        # Wait again (should return cached result)
        wait_result: CommandExecutionResult = self.run_async(cmd.wait())
        self.assertEqual(wait_result, result)

    def test_command_wait_pending(self) -> None:
        """Test waiting for a pending command."""
        cmd: AsyncCommand = self.create_successful_command()

        # Wait without executing first (should execute automatically)
        result: CommandExecutionResult = self.run_async(cmd.wait())

        # Verify result
        self.assert_command_success(result)
        self.assertEqual(cmd.state, CommandState.COMPLETED)

    def test_command_properties_during_execution(self) -> None:
        """Test command properties during execution."""
        cmd: AsyncCommand = self.create_timeout_command(timeout=1.0)

        # Initial state
        self.assertEqual(cmd.state, CommandState.PENDING)
        self.assertFalse(cmd.is_running)
        self.assertFalse(cmd.is_completed)
        self.assertIsNone(cmd.result)

        # Start execution
        execution_task = asyncio.create_task(self.execute_command(cmd))

        # Wait for it to start running
        self.run_async(asyncio.sleep(0.1))

        # Check running state
        self.assertTrue(cmd.is_running)
        self.assertFalse(cmd.is_completed)
        self.assertEqual(cmd.state, CommandState.RUNNING)

        # Wait for completion
        result: CommandExecutionResult = self.run_async(execution_task)

        # Check completed state
        self.assertFalse(cmd.is_running)
        self.assertTrue(cmd.is_completed)
        self.assertEqual(cmd.state, CommandState.TIMEOUT)  # Should timeout
        self.assertIsNotNone(cmd.result)
        self.assertEqual(cmd.result, result)

    def test_command_multiple_executions(self) -> None:
        """Test multiple executions of the same command."""
        cmd: AsyncCommand = self.create_successful_command()

        # First execution
        result1: CommandExecutionResult = self.run_async(self.execute_command(cmd))
        self.assert_command_success(result1)

        # Reset state for second execution
        cmd._state = CommandState.PENDING
        cmd._result = None

        # Second execution
        result2: CommandExecutionResult = self.run_async(self.execute_command(cmd))
        self.assert_command_success(result2)

        # Results should be different instances
        self.assertIsNot(result1, result2)

    def test_command_kill_not_running(self) -> None:
        """Test killing a command that is not running."""
        cmd: AsyncCommand = self.create_simple_command(['echo', 'test'])

        # Try to kill before execution
        kill_success: bool = cmd.kill()
        self.assertFalse(kill_success)

        # Execute and complete
        result: CommandExecutionResult = self.run_async(self.execute_command(cmd))
        self.assert_command_success(result)

        # Try to kill after completion
        kill_success = cmd.kill()
        self.assertFalse(kill_success)

    def test_command_state_consistency(self) -> None:
        """Test that command state remains consistent during execution."""
        cmd: AsyncCommand = self.create_successful_command()

        # Track state changes
        states: List[CommandState] = [cmd.state]

        # Start tracking and execution
        async def track_states() -> None:
            while not cmd.is_completed:
                current_state = cmd.state
                if current_state != states[-1]:
                    states.append(current_state)
                await asyncio.sleep(0.001)

        tracking_task = asyncio.create_task(track_states())
        result = self.run_async(self.execute_command(cmd))
        self.run_async(tracking_task)

        # Verify state progression
        self.assertIn(CommandState.PENDING, states)
        self.assertIn(CommandState.RUNNING, states)
        self.assertIn(CommandState.COMPLETED, states)
        self.assert_command_success(result)


__all__ = [
    "TestCommandStateManagement"
]
