"""
Integration tests for SystemGateway.
"""
from tests.gateways.v1.system.base import BaseSystemGatewayTest
from backend.src.schemas.v1.system import CommandResponse, CommandResult
from backend.src.gateways.v1.system_gateway import SystemGateway
import unittest
from unittest.mock import patch, MagicMock
import asyncio
import os
import tempfile
import json


class TestSystemGatewayIntegration(BaseSystemGatewayTest):
    """Integration tests for SystemGateway with real system commands."""

    def test_file_operations_integration(self):
        """Test file operations using system commands."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_file.txt")
            test_content = "Hello, World! This is a test file."

            # Create file
            if self.is_windows:
                create_cmd = f'cmd /c echo {test_content} > "{test_file}"'
            else:
                create_cmd = f'echo "{test_content}" > "{test_file}"'

            create_response = self.run_async(SystemGateway.execute_command(create_cmd))
            self.assertCommandSuccess(create_response)

            # Read file
            if self.is_windows:
                read_cmd = f'cmd /c type "{test_file}"'
            else:
                read_cmd = f'cat "{test_file}"'

            read_response = self.run_async(SystemGateway.execute_command(read_cmd))
            self.assertCommandSuccess(read_response)
            self.assertIn("Hello, World!", read_response.output)

            # List directory
            if self.is_windows:
                list_cmd = f'cmd /c dir "{temp_dir}"'
            else:
                list_cmd = f'ls "{temp_dir}"'

            list_response = self.run_async(SystemGateway.execute_command(list_cmd))
            self.assertCommandSuccess(list_response)
            self.assertIn("test_file.txt", list_response.output)

    def test_environment_variables_integration(self):
        """Test environment variable access using system commands."""
        # Test getting environment variable
        if self.is_windows:
            env_cmd = 'cmd /c echo %PATH%'
        else:
            env_cmd = 'echo $PATH'

        env_response = self.run_async(SystemGateway.execute_command(env_cmd))
        self.assertCommandSuccess(env_response)
        self.assertIsNotNone(env_response.output)
        self.assertGreater(len(env_response.output.strip()), 0)

    def test_system_info_integration(self):
        """Test getting system information using system commands."""
        # Test getting OS info
        if self.is_windows:
            os_cmd = 'cmd /c ver'
        else:
            os_cmd = 'uname -a'

        os_response = self.run_async(SystemGateway.execute_command(os_cmd))
        self.assertCommandSuccess(os_response)
        self.assertIsNotNone(os_response.output)

        # Test getting current directory
        if self.is_windows:
            pwd_cmd = 'cmd /c cd'
        else:
            pwd_cmd = 'pwd'

        pwd_response = self.run_async(SystemGateway.execute_command(pwd_cmd))
        self.assertCommandSuccess(pwd_response)
        self.assertIsNotNone(pwd_response.output)

    def test_process_management_integration(self):
        """Test process management using system commands."""
        # Test listing processes
        if self.is_windows:
            ps_cmd = 'tasklist'
        else:
            ps_cmd = 'ps aux'

        ps_response = self.run_async(SystemGateway.execute_command(ps_cmd))
        self.assertCommandSuccess(ps_response)
        self.assertIsNotNone(ps_response.output)

        # Test getting process count
        if self.is_windows:
            count_cmd = 'cmd /c tasklist | find /c /v ""'
        else:
            count_cmd = 'ps aux | wc -l'

        count_response = self.run_async(SystemGateway.execute_command(count_cmd))
        self.assertCommandSuccess(count_response)
        self.assertIsNotNone(count_response.output)

    def test_network_commands_integration(self):
        """Test network-related commands."""
        # Test ping (with short timeout to avoid long waits)
        if self.is_windows:
            ping_cmd = 'cmd /c ping -n 1 127.0.0.1'
        else:
            ping_cmd = 'ping -c 1 127.0.0.1'

        ping_response = self.run_async(SystemGateway.execute_command(ping_cmd, timeout=10.0))
        self.assertCommandSuccess(ping_response)
        self.assertIn("127.0.0.1", ping_response.output)

    def test_json_processing_integration(self):
        """Test JSON processing using system commands."""
        test_data = {"name": "test", "value": 123, "items": [1, 2, 3]}

        # Create JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            json_file = f.name

        try:
            # Read and parse JSON
            if self.is_windows:
                read_cmd = f'cmd /c type "{json_file}"'
            else:
                read_cmd = f'cat "{json_file}"'

            read_response = self.run_async(SystemGateway.execute_command(read_cmd))
            self.assertCommandSuccess(read_response)

            # Verify JSON content
            parsed_data = json.loads(read_response.output)
            self.assertEqual(parsed_data["name"], "test")
            self.assertEqual(parsed_data["value"], 123)
            self.assertEqual(parsed_data["items"], [1, 2, 3])

        finally:
            # Clean up
            os.unlink(json_file)

    def test_concurrent_file_operations_integration(self):
        """Test concurrent file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple files concurrently
            commands = []
            for i in range(5):
                test_file = os.path.join(temp_dir, f"concurrent_file_{i}.txt")
                if self.is_windows:
                    cmd = f'cmd /c echo "File {i} content" > "{test_file}"'
                else:
                    cmd = f'echo "File {i} content" > "{test_file}"'
                commands.append(cmd)

            responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

            # All should succeed
            self.assertEqual(len(responses), 5)
            for response in responses:
                self.assertCommandSuccess(response)

            # Verify files were created
            for i in range(5):
                test_file = os.path.join(temp_dir, f"concurrent_file_{i}.txt")
                self.assertTrue(os.path.exists(test_file))

    def test_error_handling_integration(self):
        """Test error handling with real system commands."""
        # Test command that doesn't exist
        invalid_response = self.run_async(SystemGateway.execute_command("nonexistent_command_12345"))
        self.assertCommandFail(invalid_response)
        self.assertIsNotNone(invalid_response.error)

        # Test command with invalid arguments
        if self.is_windows:
            invalid_args_response = self.run_async(SystemGateway.execute_command("cmd /c dir /invalid_flag"))
        else:
            invalid_args_response = self.run_async(SystemGateway.execute_command("ls --invalid-flag"))

        # This should fail with invalid arguments
        self.assertCommandFail(invalid_args_response)
        self.assertIsNotNone(invalid_args_response.error)

    def test_timeout_integration(self):
        """Test timeout with real long-running commands."""
        # Test with a command that would normally take a long time
        if self.is_windows:
            long_cmd = 'ping -n 10 127.0.0.1'
        else:
            long_cmd = 'sleep 5'

        # Test with short timeout
        timeout_response = self.run_async(
            SystemGateway.execute_command(long_cmd, timeout=1.0)
        )

        # Should timeout
        self.assertCommandFail(timeout_response)
        self.assertIn("timed out", timeout_response.error)

    def test_mixed_command_types_integration(self):
        """Test mixed command types in concurrent execution."""
        if self.is_windows:
            commands = [
                self.get_echo_command("string command"),
                self.get_echo_args("args command"),
                "cmd /c echo quoted command",
                ["cmd", "/c", "echo", "list", "command"],
                self.get_echo_command("another string")
            ]
        else:
            commands = [
                self.get_echo_command("string command"),
                self.get_echo_args("args command"),
                "echo 'quoted command'",
                ["echo", "list", "command"],
                self.get_echo_command("another string")
            ]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands))

        # All should succeed
        self.assertEqual(len(responses), 5)
        for response in responses:
            self.assertCommandSuccess(response)

    def test_large_output_integration(self):
        """Test handling of large command output."""
        # Generate large output
        if self.is_windows:
            large_cmd = 'cmd /c for /l %i in (1,1,100) do @echo Line %i'
        else:
            large_cmd = 'for i in {1..100}; do echo "Line $i"; done'

        large_response = self.run_async(SystemGateway.execute_command(large_cmd))
        self.assertCommandSuccess(large_response)
        # Windows for loop generates less output, so adjust expectation
        if self.is_windows:
            self.assertGreater(len(large_response.output), 500)  # Should have substantial output
        else:
            self.assertGreater(len(large_response.output), 1000)  # Should have substantial output

    def test_special_characters_integration(self):
        """Test commands with special characters in real scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with special characters in name
            special_file = os.path.join(temp_dir, "test file with spaces & special chars!.txt")
            special_content = "Content with special chars: !@#$%^&*()"

            if self.is_windows:
                create_cmd = f'cmd /c echo {special_content} > "{special_file}"'
            else:
                create_cmd = f'echo "{special_content}" > "{special_file}"'

            create_response = self.run_async(SystemGateway.execute_command(create_cmd))
            self.assertCommandSuccess(create_response)

            # Verify file was created
            self.assertTrue(os.path.exists(special_file))

    def test_unicode_integration(self):
        """Test unicode handling in real scenarios."""
        unicode_content = "Unicode test: 你好世界 🌍 café naïve résumé"

        if self.is_windows:
            unicode_cmd = f'cmd /c echo {unicode_content}'
        else:
            unicode_cmd = f'echo "{unicode_content}"'

        unicode_response = self.run_async(SystemGateway.execute_command(unicode_cmd))
        self.assertCommandSuccess(unicode_response)
        self.assertIsNotNone(unicode_response.output)

    def test_performance_integration(self):
        """Test performance with multiple concurrent operations."""
        # Test with many concurrent commands
        commands = [self.get_echo_command(f"perf test {i}") for i in range(50)]

        responses = self.run_async(SystemGateway.execute_multiple_commands(commands, max_concurrent=10))

        # All should succeed
        self.assertEqual(len(responses), 50)
        for i, response in enumerate(responses):
            self.assertCommandSuccess(response)
            self.assertIn(f"perf test {i}", response.output)

    def test_resource_cleanup_integration(self):
        """Test that resources are properly cleaned up."""
        # Execute many commands to test resource cleanup
        commands = [self.get_echo_command(f"cleanup test {i}") for i in range(20)]

        # Run multiple batches
        for batch in range(5):
            responses = self.run_async(SystemGateway.execute_multiple_commands(commands))
            self.assertEqual(len(responses), 20)

            for response in responses:
                self.assertCommandSuccess(response)

        # If we get here without memory issues, cleanup is working

    def test_cross_platform_compatibility_integration(self):
        """Test cross-platform compatibility."""
        # Test basic commands that should work on both platforms
        if self.is_windows:
            basic_commands = [
                "cmd /c echo cross platform test",
                ["cmd", "/c", "echo", "cross", "platform", "test"]
            ]
        else:
            basic_commands = [
                "echo 'cross platform test'",
                ["echo", "cross", "platform", "test"]
            ]

        for command in basic_commands:
            if isinstance(command, str):
                response = self.run_async(SystemGateway.execute_command(command))
            else:
                response = self.run_async(SystemGateway.execute_command_args(command))

            self.assertCommandSuccess(response)
            self.assertIn("cross platform test", response.output)


__all__ = [
    "TestSystemGatewayIntegration"
]
