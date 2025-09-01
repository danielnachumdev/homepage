"""
Command executor for the new command-based system.

This module provides the CommandExecutor class that executes Command objects
and returns CommandResult objects with full execution details.
"""

import time
import subprocess
from pathlib import Path
from typing import List, Optional
from .commands import Command, CommandResult
from .process_manager import ProcessManager


class CommandExecutor:
    """
    Executes Command objects and returns detailed results.

    This class handles the execution of individual commands with retry logic,
    timeout handling, and comprehensive result reporting.
    """

    def __init__(self, logger):
        """
        Initialize the CommandExecutor.

        Args:
            logger: Logger instance for logging command execution
        """
        self.logger = logger

    def execute_command(self, command: Command) -> CommandResult:
        """
        Execute a single command with retry logic and timeout handling.

        Args:
            command: The Command object to execute

        Returns:
            CommandResult: Detailed result of command execution
        """
        retry_count = 0
        max_retries = command.retry_count or 0

        while retry_count <= max_retries:
            start_time = time.time()

            try:
                self.logger.info("Executing command: %s",
                                 command.description or str(command.command))

                # Execute the command using ProcessManager
                result = ProcessManager.spawn(
                    command=command.command,
                    detached=False,
                    cwd=command.cwd
                )

                if not result.success or not result.process:
                    error_msg = result.error_message or "Failed to start process"
                    execution_time = time.time() - start_time

                    return CommandResult(
                        command=command,
                        success=False,
                        return_code=-1,
                        stdout="",
                        stderr=error_msg,
                        execution_time=execution_time,
                        retry_count=retry_count,
                        error_message=error_msg
                    )

                # Wait for the process to complete
                stdout, stderr = result.process.communicate()
                execution_time = time.time() - start_time

                # Convert bytes to string if needed
                if isinstance(stdout, bytes):
                    stdout = stdout.decode('utf-8', errors='replace')
                if isinstance(stderr, bytes):
                    stderr = stderr.decode('utf-8', errors='replace')

                return_code = result.process.returncode or 0
                success = return_code == 0

                # Log the result
                if success:
                    self.logger.info(
                        "Command completed successfully in %.2f seconds", execution_time)
                else:
                    self.logger.warning("Command failed with return code %d in %.2f seconds",
                                        return_code, execution_time)

                if stdout:
                    self.logger.debug("Command stdout: %s", stdout)
                if stderr:
                    self.logger.debug("Command stderr: %s", stderr)

                return CommandResult(
                    command=command,
                    success=success,
                    return_code=return_code,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=execution_time,
                    retry_count=retry_count
                )

            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = f"Exception during command execution: {str(e)}"

                self.logger.error("Command execution failed: %s", error_msg)

                if retry_count < max_retries:
                    retry_count += 1
                    self.logger.info(
                        "Retrying command (attempt %d/%d)", retry_count, max_retries)
                    time.sleep(1)  # Brief delay before retry
                    continue

                return CommandResult(
                    command=command,
                    success=False,
                    return_code=-1,
                    stdout="",
                    stderr=error_msg,
                    execution_time=execution_time,
                    retry_count=retry_count,
                    error_message=error_msg
                )

        # This should never be reached, but just in case
        return CommandResult(
            command=command,
            success=False,
            return_code=-1,
            stdout="",
            stderr="Maximum retries exceeded",
            execution_time=0.0,
            retry_count=retry_count,
            error_message="Maximum retries exceeded"
        )

    def execute_commands(self, commands: List[Command], step_name: str) -> 'StepExecutionResult':
        """
        Execute a list of commands in sequence.

        Args:
            commands: List of Command objects to execute
            step_name: Name of the step for logging and result tracking

        Returns:
            StepExecutionResult: Overall result of executing all commands
        """
        from .commands import StepExecutionResult

        start_time = time.time()
        command_results = []
        failed_commands = []

        self.logger.info(
            "Starting execution of step: %s (%d commands)", step_name, len(commands))

        for i, command in enumerate(commands, 1):
            self.logger.info("Executing command %d/%d: %s",
                             i, len(commands), command.description or str(command.command))

            result = self.execute_command(command)
            command_results.append(result)

            if not result.success:
                failed_commands.append(result)

                # If this is a required command, stop execution
                if command.required:
                    self.logger.error(
                        "Required command failed, stopping step execution")
                    break

        total_execution_time = time.time() - start_time
        success = len(failed_commands) == 0 or not any(
            cmd.command.required for cmd in failed_commands)

        if success:
            self.logger.info("Step '%s' completed successfully in %.2f seconds",
                             step_name, total_execution_time)
        else:
            self.logger.error("Step '%s' failed after %.2f seconds",
                              step_name, total_execution_time)

        return StepExecutionResult(
            step_name=step_name,
            success=success,
            command_results=command_results,
            total_execution_time=total_execution_time,
            failed_commands=failed_commands,
            error_message=f"Step failed: {len(failed_commands)} commands failed" if not success else None
        )


__all__ = [
    "CommandExecutor"
]
