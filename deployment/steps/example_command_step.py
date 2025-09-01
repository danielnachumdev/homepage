"""
Example step demonstrating the new command-based approach.

This step shows how to create a step using the new command-based system
where you just return lists of Command objects instead of implementing
complex execution logic.
"""

from pathlib import Path
from typing import List
from .base_step import Step
from ..utils.commands import Command


class ExampleCommandStep(Step):
    """
    Example step that demonstrates the command-based approach.

    This step shows how simple it is to create a step by just defining
    the commands to execute for install, uninstall, and validate operations.
    """

    def __init__(self,
                 project_root: str = ".",
                 name: str = "example-command-step",
                 description: str = "Example step using command-based approach"):
        """
        Initialize the example command step.

        Args:
            project_root: Path to the project root directory
            name: Name of the step
            description: Description of what this step does
        """
        super().__init__(name, description)
        self.project_root = Path(project_root)

    def get_install_commands(self) -> List[Command]:
        """
        Get commands to execute for installation.

        Returns:
            List of Command objects to execute in order
        """
        return [
            Command(
                command="echo 'Starting installation'",
                description="Log installation start",
                required=True
            ),
            Command(
                command="mkdir -p logs",
                description="Create logs directory",
                required=True,
                cwd=self.project_root
            ),
            Command(
                command="echo 'Installation complete' > logs/install.log",
                description="Create installation log file",
                required=True,
                cwd=self.project_root
            ),
            Command(
                command="echo 'Installation successful'",
                description="Log installation success",
                required=True
            )
        ]

    def get_uninstall_commands(self) -> List[Command]:
        """
        Get commands to execute for uninstallation.

        Returns:
            List of Command objects to execute in order
        """
        return [
            Command(
                command="echo 'Starting uninstallation'",
                description="Log uninstallation start",
                required=True
            ),
            Command(
                command="rm -f logs/install.log",
                description="Remove installation log file",
                required=False,  # Not required - might not exist
                cwd=self.project_root
            ),
            Command(
                command="echo 'Uninstallation complete'",
                description="Log uninstallation success",
                required=True
            )
        ]

    def get_validate_commands(self) -> List[Command]:
        """
        Get commands to execute for validation.

        Returns:
            List of Command objects to execute in order
        """
        return [
            Command(
                command="echo 'Validating environment'",
                description="Log validation start",
                required=True
            ),
            Command(
                command="test -d logs",
                description="Check if logs directory exists",
                required=True,
                cwd=self.project_root,
                expected=0  # Expect return code 0 for success
            ),
            Command(
                command="echo 'Validation complete'",
                description="Log validation success",
                required=True
            )
        ]


__all__ = [
    "ExampleCommandStep"
]
