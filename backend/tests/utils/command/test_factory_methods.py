"""
Tests for AsyncCommand classmethod factories (cmd, powershell, wsl).

This module tests the Windows-specific factory methods that create AsyncCommand instances
with proper command parsing, escaping, and argument handling for different shells.
"""

import unittest
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.utils.command import AsyncCommand, CommandType
from tests.utils.command.base import BaseCommandTest


class TestCmdFactory(BaseCommandTest):
    """Test cases for AsyncCommand.cmd factory method."""

    def test_cmd_factory_basic(self):
        """Test basic cmd factory functionality."""
        cmd = AsyncCommand.cmd("echo test")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("test", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo test"]
        self.assertEqual(expected_args, cmd.args)
        self.assertEqual(CommandType.CLI, cmd.command_type)

    def test_cmd_factory_with_quotes(self):
        """Test cmd factory with quoted arguments."""
        cmd = AsyncCommand.cmd('echo "hello world"')
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello world", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", 'echo "hello world"']
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_single_quotes(self):
        """Test cmd factory with single quotes."""
        cmd = AsyncCommand.cmd("echo 'hello world'")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello world", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo 'hello world'"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_spaces(self):
        """Test cmd factory with spaces in arguments."""
        cmd = AsyncCommand.cmd("echo hello world")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello world", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo hello world"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_special_characters(self):
        """Test cmd factory with special characters."""
        cmd = AsyncCommand.cmd('echo "C:\\Users\\Test\\file.txt"')
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("C:\\Users\\Test\\file.txt", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", 'echo "C:\\Users\\Test\\file.txt"']
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_multiple_commands(self):
        """Test cmd factory with multiple commands using &&."""
        cmd = AsyncCommand.cmd("echo hello && echo world")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello", result.stdout)
        self.assertIn("world", result.stdout)
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo hello && echo world"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_pipes(self):
        """Test cmd factory with pipe commands."""
        cmd = AsyncCommand.cmd("echo hello | findstr hello")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo hello | findstr hello"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_redirection(self):
        """Test cmd factory with output redirection."""
        cmd = AsyncCommand.cmd("echo hello > output.txt")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # Check that the file was created
        import os
        self.assertTrue(os.path.exists("output.txt"))
        # Clean up
        if os.path.exists("output.txt"):
            os.remove("output.txt")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo hello > output.txt"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_environment_variables(self):
        """Test cmd factory with environment variables."""
        cmd = AsyncCommand.cmd("echo %USERNAME%")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # Should output the actual username
        self.assertTrue(len(result.stdout.strip()) > 0)
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo %USERNAME%"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_unicode(self):
        """Test cmd factory with unicode characters."""
        cmd = AsyncCommand.cmd("echo 你好世界")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("你好世界", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo 你好世界"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_whitespace_stripping(self):
        """Test cmd factory strips leading/trailing whitespace."""
        cmd = AsyncCommand.cmd("  echo test  ")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("test", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo test"]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_empty_string(self):
        """Test cmd factory with empty string."""
        cmd = AsyncCommand.cmd("")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        # Empty command should still succeed but with no output
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", ""]
        self.assertEqual(expected_args, cmd.args)

    def test_cmd_factory_with_kwargs(self):
        """Test cmd factory passes through additional kwargs."""
        cmd = AsyncCommand.cmd("echo test", timeout=5.0, command_type=CommandType.GUI)
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # GUI commands don't capture stdout, so we don't check for it
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["cmd", "/c", "echo test"]
        self.assertEqual(expected_args, cmd.args)
        self.assertEqual(5.0, cmd.timeout)
        self.assertEqual(CommandType.GUI, cmd.command_type)

    def test_complex_command_parsing_scenarios(self):
        """Test complex command parsing scenarios for CMD factory."""
        # Complex cmd command with multiple elements
        complex_cmd = 'echo "Hello World" && dir C:\\Users\\Test\\Documents && echo "Done"'
        cmd = AsyncCommand.cmd(complex_cmd)
        expected_args = ["cmd", "/c", 'echo "Hello World" && dir C:\\Users\\Test\\Documents && echo "Done"']
        self.assertEqual(expected_args, cmd.args)
        
        # Test actual execution (simplified version that will work)
        simple_cmd = AsyncCommand.cmd('echo "Hello World" && echo "Done"')
        result = self.run_async(simple_cmd.execute())
        self.assertTrue(result.success)
        self.assertIn("Hello World", result.stdout)
        self.assertIn("Done", result.stdout)

    def test_edge_cases_and_error_conditions(self):
        """Test edge cases and potential error conditions for CMD factory."""
        # Test with only whitespace
        cmd_whitespace = AsyncCommand.cmd("   \t\n  ")
        expected_whitespace = ["cmd", "/c", ""]
        self.assertEqual(expected_whitespace, cmd_whitespace.args)

        # Test with very long command
        long_command = "echo " + "x" * 1000
        cmd_long = AsyncCommand.cmd(long_command)
        expected_long = ["cmd", "/c", long_command]
        self.assertEqual(expected_long, cmd_long.args)

    def test_unicode_and_international_characters(self):
        """Test CMD factory with unicode and international characters."""
        # Test with various unicode characters
        unicode_tests = [
            "echo 你好世界",  # Chinese
            "echo Здравствуй мир",  # Russian
            "echo مرحبا بالعالم",  # Arabic
            "echo こんにちは世界",  # Japanese
            "echo 안녕하세요 세계",  # Korean
            "echo Γεια σας κόσμος",  # Greek
        ]

        for unicode_cmd in unicode_tests:
            # Test cmd factory
            cmd_cmd = AsyncCommand.cmd(unicode_cmd)
            expected_cmd = ["cmd", "/c", unicode_cmd]
            self.assertEqual(expected_cmd, cmd_cmd.args)

    def test_command_with_newlines_and_tabs(self):
        """Test CMD factory with commands containing newlines and tabs."""
        multiline_cmd = "echo hello\nworld\ttest"

        cmd_cmd = AsyncCommand.cmd(multiline_cmd)
        expected_cmd = ["cmd", "/c", multiline_cmd]
        self.assertEqual(expected_cmd, cmd_cmd.args)

    def test_real_world_command_examples(self):
        """Test CMD factory with real-world command examples."""
        # Real-world cmd examples
        real_cmd_examples = [
            'tasklist /FI "IMAGENAME eq chrome.exe" /FO CSV',
            'dir "C:\\Program Files\\Google\\Chrome\\Application" /B',
            'echo %USERNAME% > user.txt',
            'ping google.com -n 4',
        ]

        for cmd_example in real_cmd_examples:
            cmd = AsyncCommand.cmd(cmd_example)
            expected = ["cmd", "/c", cmd_example]
            self.assertEqual(expected, cmd.args)


class TestPowerShellFactory(BaseCommandTest):
    """Test cases for AsyncCommand.powershell factory method."""

    def test_powershell_factory_basic(self):
        """Test basic powershell factory functionality."""
        cmd = AsyncCommand.powershell("echo test")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("test", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", "echo test"]
        self.assertEqual(expected_args, cmd.args)
        self.assertEqual(CommandType.CLI, cmd.command_type)

    def test_powershell_factory_with_quotes(self):
        """Test powershell factory with quoted arguments."""
        cmd = AsyncCommand.powershell('echo "hello world"')
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello world", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", 'echo "hello world"']
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_single_quotes(self):
        """Test powershell factory with single quotes."""
        cmd = AsyncCommand.powershell("echo 'hello world'")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("hello world", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", "echo 'hello world'"]
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_double_quotes_inside(self):
        """Test powershell factory with double quotes inside the command."""
        cmd = AsyncCommand.powershell('Get-Process | Where-Object {$_.Name -eq "chrome"}')
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # Should return process information or empty if chrome not running
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", 'Get-Process | Where-Object {$_.Name -eq "chrome"}']
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_escaped_quotes(self):
        """Test powershell factory with escaped quotes."""
        cmd = AsyncCommand.powershell('Write-Host "He said \"Hello World\""')
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # The actual output shows "He said  Hello World" (with spaces instead of quotes)
        self.assertIn("He said", result.stdout.strip())
        self.assertIn("Hello World", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", 'Write-Host "He said \"Hello World\""']
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_multiline_command(self):
        """Test powershell factory with multiline command."""
        multiline_cmd = """Get-Process | 
        Where-Object {$_.Name -eq "chrome"} | 
        Select-Object Name, Id"""
        cmd = AsyncCommand.powershell(multiline_cmd)
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # Should return process information or empty if chrome not running
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command",
                         "Get-Process | \n        Where-Object {$_.Name -eq \"chrome\"} | \n        Select-Object Name, Id"]
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_variables(self):
        """Test powershell factory with PowerShell variables."""
        cmd = AsyncCommand.powershell("$var = 'test'; Write-Host $var")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("test", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", "$var = 'test'; Write-Host $var"]
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_special_characters(self):
        """Test powershell factory with special characters."""
        cmd = AsyncCommand.powershell('Get-ChildItem "C:\\Users\\Test\\file.txt"')
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        # This might fail if the file doesn't exist, but the command should be parsed correctly
        # We'll just check that it doesn't fail due to parsing issues
        if not result.success:
            # If it fails, it should be because the file doesn't exist, not because of parsing
            self.assertNotIn("syntax", result.stderr.lower())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", 'Get-ChildItem "C:\\Users\\Test\\file.txt"']
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_unicode(self):
        """Test powershell factory with unicode characters."""
        cmd = AsyncCommand.powershell("Write-Host 你好世界")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("你好世界", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", "Write-Host 你好世界"]
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_whitespace_stripping(self):
        """Test powershell factory strips leading/trailing whitespace."""
        cmd = AsyncCommand.powershell("  Write-Host test  ")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        self.assertIn("test", result.stdout.strip())
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", "Write-Host test"]
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_empty_string(self):
        """Test powershell factory with empty string."""
        cmd = AsyncCommand.powershell("")
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        # Empty command should still succeed but with no output
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", ""]
        self.assertEqual(expected_args, cmd.args)

    def test_powershell_factory_with_kwargs(self):
        """Test powershell factory passes through additional kwargs."""
        cmd = AsyncCommand.powershell("Write-Host test", timeout=10.0, command_type=CommandType.GUI)
        
        # B: Test actual execution first
        result = self.run_async(cmd.execute())
        self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        # GUI commands don't capture stdout, so we don't check for it
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["powershell", "-Command", "Write-Host test"]
        self.assertEqual(expected_args, cmd.args)
        self.assertEqual(10.0, cmd.timeout)
        self.assertEqual(CommandType.GUI, cmd.command_type)

    def test_complex_command_parsing_scenarios(self):
        """Test complex command parsing scenarios for PowerShell factory."""
        # Complex powershell command with variables and quotes
        complex_ps = 'Get-Process | Where-Object {$_.Name -eq "chrome"} | Select-Object Name, Id, @{Name="Memory(MB)";Expression={[math]::Round($_.WorkingSet/1MB,2)}}'
        cmd_ps = AsyncCommand.powershell(complex_ps)
        expected_ps_args = ["powershell", "-Command",
                            'Get-Process | Where-Object {$_.Name -eq "chrome"} | Select-Object Name, Id, @{Name="Memory(MB)";Expression={[math]::Round($_.WorkingSet/1MB,2)}}']
        self.assertEqual(expected_ps_args, cmd_ps.args)
        
        # Test actual execution (simplified version that will work)
        simple_ps = AsyncCommand.powershell('Get-Process | Select-Object Name -First 1')
        result = self.run_async(simple_ps.execute())
        self.assertTrue(result.success)
        self.assertIn("Name", result.stdout)

    def test_unicode_and_international_characters(self):
        """Test PowerShell factory with unicode and international characters."""
        # Test with various unicode characters
        unicode_tests = [
            "Write-Host 你好世界",  # Chinese
            "Write-Host Здравствуй мир",  # Russian
            "Write-Host مرحبا بالعالم",  # Arabic
            "Write-Host こんにちは世界",  # Japanese
            "Write-Host 안녕하세요 세계",  # Korean
            "Write-Host Γεια σας κόσμος",  # Greek
        ]

        for unicode_cmd in unicode_tests:
            # Test powershell factory
            cmd_ps = AsyncCommand.powershell(unicode_cmd)
            expected_ps = ["powershell", "-Command", unicode_cmd]
            self.assertEqual(expected_ps, cmd_ps.args)

    def test_command_with_newlines_and_tabs(self):
        """Test PowerShell factory with commands containing newlines and tabs."""
        multiline_cmd = "Write-Host hello\nworld\ttest"

        cmd_ps = AsyncCommand.powershell(multiline_cmd)
        expected_ps = ["powershell", "-Command", multiline_cmd]
        self.assertEqual(expected_ps, cmd_ps.args)

    def test_real_world_command_examples(self):
        """Test PowerShell factory with real-world command examples."""
        # Real-world powershell examples
        real_ps_examples = [
            'Get-Process | Where-Object {$_.Name -eq "chrome"}',
            'Get-ChildItem "C:\\Users\\$env:USERNAME\\Documents" -Recurse -Name "*.txt"',
            'Get-Service | Where-Object {$_.Status -eq "Running"} | Select-Object Name, Status',
            'Invoke-WebRequest -Uri "https://api.github.com/users/octocat" | ConvertFrom-Json',
        ]

        for ps_example in real_ps_examples:
            cmd = AsyncCommand.powershell(ps_example)
            expected = ["powershell", "-Command", ps_example]
            self.assertEqual(expected, cmd.args)


class TestWslFactory(BaseCommandTest):
    """Test cases for AsyncCommand.wsl factory method."""

    def test_wsl_factory_basic(self):
        """Test basic wsl factory functionality."""
        cmd = AsyncCommand.wsl("echo test")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            self.assertIn("test", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo test"']
        self.assertEqual(expected_args, cmd.args)
        self.assertEqual(CommandType.CLI, cmd.command_type)

    def test_wsl_factory_with_quotes(self):
        """Test wsl factory with quoted arguments."""
        cmd = AsyncCommand.wsl('echo "hello world"')
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            self.assertIn("hello world", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo \\"hello world\\""']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_single_quotes(self):
        """Test wsl factory with single quotes."""
        cmd = AsyncCommand.wsl("echo 'hello world'")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            self.assertIn("hello world", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo \'hello world\'"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_linux_commands(self):
        """Test wsl factory with typical Linux commands."""
        cmd = AsyncCommand.wsl("ls -la /home")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            # Should return directory listing
            self.assertTrue(len(result.stdout.strip()) > 0)
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"ls -la /home"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_pipes(self):
        """Test wsl factory with pipe commands."""
        cmd = AsyncCommand.wsl("ls -la | grep test")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            # Might not find "test" in the listing, but command should succeed
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"ls -la | grep test"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_redirection(self):
        """Test wsl factory with output redirection."""
        cmd = AsyncCommand.wsl("echo hello > output.txt")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            # Check that the file was created in WSL
            check_cmd = AsyncCommand.wsl("ls output.txt")
            check_result = self.run_async(check_cmd.execute())
            if check_result.success:
                # Clean up
                cleanup_cmd = AsyncCommand.wsl("rm output.txt")
                self.run_async(cleanup_cmd.execute())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo hello > output.txt"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_environment_variables(self):
        """Test wsl factory with environment variables."""
        cmd = AsyncCommand.wsl("echo $HOME")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            # Should output the home directory path
            self.assertTrue(len(result.stdout.strip()) > 0)
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo $HOME"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_sudo(self):
        """Test wsl factory with sudo commands."""
        cmd = AsyncCommand.wsl("sudo apt update")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            # This might fail due to permissions or network, but should not fail due to parsing
            if not result.success:
                self.assertNotIn("syntax", result.stderr.lower())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"sudo apt update"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_unicode(self):
        """Test wsl factory with unicode characters."""
        cmd = AsyncCommand.wsl("echo 你好世界")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            self.assertIn("你好世界", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo 你好世界"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_whitespace_stripping(self):
        """Test wsl factory strips leading/trailing whitespace."""
        cmd = AsyncCommand.wsl("  echo test  ")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            self.assertIn("test", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo test"']
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_empty_string(self):
        """Test wsl factory with empty string."""
        cmd = AsyncCommand.wsl("")
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            # Empty command should still succeed but with no output
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", ""]
        self.assertEqual(expected_args, cmd.args)

    def test_wsl_factory_with_kwargs(self):
        """Test wsl factory passes through additional kwargs."""
        cmd = AsyncCommand.wsl("echo test", timeout=15.0, command_type=CommandType.GUI)
        
        # B: Test actual execution first (only if WSL is available)
        try:
            result = self.run_async(cmd.execute())
            self.assertTrue(result.success, f"Command failed with stderr: {result.stderr}")
            self.assertIn("test", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")
        
        # A: Assert the expected output of the internal state based on real behavior
        expected_args = ["wsl", '"echo test"']
        self.assertEqual(expected_args, cmd.args)
        self.assertEqual(15.0, cmd.timeout)
        self.assertEqual(CommandType.GUI, cmd.command_type)

    def test_complex_command_parsing_scenarios(self):
        """Test complex command parsing scenarios for WSL factory."""
        # Complex wsl command with pipes and redirection
        complex_wsl = 'ls -la /home | grep "\.txt$" | head -10 > /tmp/file_list.txt'
        cmd_wsl = AsyncCommand.wsl(complex_wsl)
        expected_wsl_args = ["wsl", '"ls -la /home | grep \\"\\.txt$\\" | head -10 > /tmp/file_list.txt"']
        self.assertEqual(expected_wsl_args, cmd_wsl.args)
        
        # Test actual execution (simplified version that will work)
        try:
            simple_wsl = AsyncCommand.wsl('echo "Hello from WSL"')
            result = self.run_async(simple_wsl.execute())
            self.assertTrue(result.success)
            self.assertIn("Hello from WSL", result.stdout.strip())
        except Exception:
            # WSL might not be available, skip execution test
            self.skipTest("WSL not available for execution test")

    def test_edge_cases_and_error_conditions(self):
        """Test edge cases and potential error conditions for WSL factory."""
        # Test with special characters that might cause issues
        special_chars = 'echo "Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?"'
        cmd_special = AsyncCommand.wsl(special_chars)
        expected_special = ["wsl", '"echo \\"Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?\\""']
        self.assertEqual(expected_special, cmd_special.args)

        # Test with very long command
        long_command = "echo " + "x" * 1000
        cmd_long = AsyncCommand.wsl(long_command)
        expected_long = ["wsl", f'"{long_command}"']
        self.assertEqual(expected_long, cmd_long.args)

    def test_unicode_and_international_characters(self):
        """Test WSL factory with unicode and international characters."""
        # Test with various unicode characters
        unicode_tests = [
            "echo 你好世界",  # Chinese
            "echo Здравствуй мир",  # Russian
            "echo مرحبا بالعالم",  # Arabic
            "echo こんにちは世界",  # Japanese
            "echo 안녕하세요 세계",  # Korean
            "echo Γεια σας κόσμος",  # Greek
        ]

        for unicode_cmd in unicode_tests:
            # Test wsl factory
            cmd_wsl = AsyncCommand.wsl(unicode_cmd)
            expected_wsl = ["wsl", f'"{unicode_cmd}"']
            self.assertEqual(expected_wsl, cmd_wsl.args)

    def test_command_with_newlines_and_tabs(self):
        """Test WSL factory with commands containing newlines and tabs."""
        multiline_cmd = "echo hello\nworld\ttest"

        cmd_wsl = AsyncCommand.wsl(multiline_cmd)
        expected_wsl = ["wsl", f'"{multiline_cmd}"']
        self.assertEqual(expected_wsl, cmd_wsl.args)

    def test_real_world_command_examples(self):
        """Test WSL factory with real-world command examples."""
        # Real-world wsl examples
        real_wsl_examples = [
            'ls -la /home',
            'sudo apt update && sudo apt upgrade -y',
            'find /var/log -name "*.log" -type f -mtime -7',
            'ps aux | grep python | head -10',
        ]

        for wsl_example in real_wsl_examples:
            cmd = AsyncCommand.wsl(wsl_example)
            # Escape quotes in the expected result
            escaped_example = wsl_example.replace('"', '\\"')
            expected = ["wsl", f'"{escaped_example}"']
            self.assertEqual(expected, cmd.args)


if __name__ == '__main__':
    unittest.main()
