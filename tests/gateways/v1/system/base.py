"""
Base test classes for system gateway testing.
"""
from typing import List
import platform

from backend.src.schemas.v1.system import CommandHandle
from ....base import BaseTest


class BaseSystemGatewayTest(BaseTest):
    """Base test class for all system gateway tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()

        # Platform-specific command helpers
        self.is_windows = platform.system() == "Windows"
        self.echo_cmd = "echo" if self.is_windows else "echo"
        self.dir_cmd = "dir" if self.is_windows else "ls"
        self.sleep_cmd = "timeout" if self.is_windows else "sleep"

    def get_echo_command(self, text: str) -> str:
        """Get platform-specific echo command."""
        if self.is_windows:
            return f'echo {text}'
        else:
            return f'echo "{text}"'

    def get_echo_args(self, text: str) -> List[str]:
        """Get platform-specific echo command arguments."""
        if self.is_windows:
            return ["echo", text]
        else:
            return ["echo", text]

    def get_sleep_command(self, seconds: int) -> str:
        """Get platform-specific sleep command."""
        if self.is_windows:
            return f'timeout /t {seconds} /nobreak'
        else:
            return f'sleep {seconds}'

    def get_sleep_args(self, seconds: int) -> List[str]:
        """Get platform-specific sleep command arguments."""
        if self.is_windows:
            return ["timeout", "/t", str(seconds), "/nobreak"]
        else:
            return ["sleep", str(seconds)]

    def get_invalid_command(self) -> str:
        """Get a command that will definitely fail."""
        return "nonexistent_command_that_should_fail_12345"

    def get_invalid_args(self) -> List[str]:
        """Get arguments for a command that will definitely fail."""
        return ["nonexistent_command_that_should_fail_12345"]




__all__ = [
    "BaseSystemGatewayTest"
]
