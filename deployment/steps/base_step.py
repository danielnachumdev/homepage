"""
Base Step class for deployment operations.

A Step represents a single autonomous operation that can be installed or uninstalled.
Each step should be self-contained and reversible.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Type
from pathlib import Path
from deployment.utils.logger import setup_logger
from backend.src.utils.command import AsyncCommand, CommandExecutionResult


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

    @property
    def is_installed(self) -> bool:
        """Check if this step is currently installed."""
        return self._installed

    @abstractmethod
    async def install(self) -> bool:
        """
        Install this step asynchronously.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        raise NotImplementedError(
            "Subclasses must implement install method")

    @abstractmethod
    async def uninstall(self) -> bool:
        """
        Uninstall this step asynchronously.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        raise NotImplementedError(
            "Subclasses must implement uninstall method")

    @abstractmethod
    async def validate(self) -> bool:
        """
        Validate this step asynchronously.

        Returns:
            bool: True if validation passes, False otherwise
        """
        raise NotImplementedError(
            "Subclasses must implement validate method")


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
