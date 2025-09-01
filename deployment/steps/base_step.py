"""
Base Step class for deployment operations.

A Step represents a single autonomous operation that can be installed or uninstalled.
Each step should be self-contained and reversible.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Type
from deployment.utils.logger import setup_logger
from deployment.utils.commands import Command
from deployment.utils.command_executor_v2 import CommandExecutor


class Step(ABC):
    """
    Abstract base class for deployment steps.

    Each step represents a single autonomous operation that can be installed
    or uninstalled. Steps should be self-contained and reversible.
    """

    # Registry of all concrete step classes
    _steps: List[Type['Step']] = []

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register concrete (non-abstract) step subclasses.

        This method is called when a subclass is created. It automatically
        adds concrete subclasses to the registry.
        """
        super().__init_subclass__(**kwargs)

        # Check if this is a concrete class (not abstract)
        if not getattr(cls, '__abstractmethods__', None):
            # Add to registry if not already present
            if cls not in cls._steps:
                cls._steps.append(cls)

    @classmethod
    def get_registered_steps(cls) -> List[Type['Step']]:
        """
        Get all registered concrete step classes.

        Returns:
            List of concrete step classes
        """
        return cls._steps.copy()

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a step.

        Args:
            name: Unique name for this step
            description: Optional description of what this step does
        """
        self.name = name
        self.description = description or f"Step: {name}"
        self.logger = setup_logger(f"step.{name}")
        self._installed = False
        self._command_executor = CommandExecutor(self.logger)

    @property
    def is_installed(self) -> bool:
        """Check if this step is currently installed."""
        return self._installed

    @abstractmethod
    def get_install_commands(self) -> List[Command]:
        """
        Get the list of commands to execute for installation.

        Returns:
            List[Command]: Commands to execute in order for installation
        """
        raise NotImplementedError(
            "Subclasses must implement get_install_commands method")

    @abstractmethod
    def get_uninstall_commands(self) -> List[Command]:
        """
        Get the list of commands to execute for uninstallation.

        Returns:
            List[Command]: Commands to execute in order for uninstallation
        """
        raise NotImplementedError(
            "Subclasses must implement get_uninstall_commands method")

    @abstractmethod
    def get_validate_commands(self) -> List[Command]:
        """
        Get the list of commands to execute for validation.

        Returns:
            List[Command]: Commands to execute in order for validation
        """
        raise NotImplementedError(
            "Subclasses must implement get_validate_commands method")

    def install(self) -> bool:
        """
        Install this step by executing install commands.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info("Starting installation of step: %s", self.name)

        commands = self.get_install_commands()
        if not commands:
            self.logger.warning(
                "No install commands defined for step: %s", self.name)
            self._mark_installed()
            return True

        result = self._command_executor.execute_commands(
            commands, f"{self.name}_install")

        if result.success:
            self._mark_installed()
            self.logger.info("Step '%s' installed successfully", self.name)
        else:
            self.logger.error("Step '%s' installation failed", self.name)

        return result.success

    def uninstall(self) -> bool:
        """
        Uninstall this step by executing uninstall commands.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Starting uninstallation of step: %s", self.name)

        commands = self.get_uninstall_commands()
        if not commands:
            self.logger.warning(
                "No uninstall commands defined for step: %s", self.name)
            self._mark_uninstalled()
            return True

        result = self._command_executor.execute_commands(
            commands, f"{self.name}_uninstall")

        if result.success:
            self._mark_uninstalled()
            self.logger.info("Step '%s' uninstalled successfully", self.name)
        else:
            self.logger.error("Step '%s' uninstallation failed", self.name)

        return result.success

    def validate(self) -> bool:
        """
        Validate this step by executing validation commands.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Starting validation of step: %s", self.name)

        commands = self.get_validate_commands()
        if not commands:
            self.logger.warning(
                "No validation commands defined for step: %s", self.name)
            return True

        result = self._command_executor.execute_commands(
            commands, f"{self.name}_validate")

        if result.success:
            self.logger.info("Step '%s' validation passed", self.name)
        else:
            self.logger.error("Step '%s' validation failed", self.name)

        return result.success

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this step.

        Returns:
            Dict containing step metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "installed": self._installed,
            "type": self.__class__.__name__
        }

    def _mark_installed(self) -> None:
        """Mark this step as installed."""
        self._installed = True
        self.logger.info(f"Step '{self.name}' marked as installed")

    def _mark_uninstalled(self) -> None:
        """Mark this step as uninstalled."""
        self._installed = False
        self.logger.info(f"Step '{self.name}' marked as uninstalled")

    def __str__(self) -> str:
        """String representation of the step."""
        status = "installed" if self._installed else "not installed"
        return f"{self.__class__.__name__}({self.name}, {status})"

    def __repr__(self) -> str:
        """Detailed string representation of the step."""
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}', installed={self._installed})"


__all__ = [
    "Step"
]
