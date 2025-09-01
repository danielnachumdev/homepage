"""
Base Step class for deployment operations.

A Step represents a single autonomous operation that can be installed or uninstalled.
Each step should be self-contained and reversible.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from deployment.utils.logger import setup_logger


class Step(ABC):
    """
    Abstract base class for deployment steps.

    Each step represents a single autonomous operation that can be installed
    or uninstalled. Steps should be self-contained and reversible.
    """

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

    @property
    def is_installed(self) -> bool:
        """Check if this step is currently installed."""
        return self._installed

    @abstractmethod
    def install(self) -> bool:
        """
        Install this step.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement install method")

    @abstractmethod
    def uninstall(self) -> bool:
        """
        Uninstall this step.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement uninstall method")

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate that this step can be executed in the current environment.

        Returns:
            bool: True if validation passes, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate method")

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
