"""
Base Strategy class for deployment operations.

A Strategy is an ordered collection of steps that can be installed or uninstalled
in sequence. Uninstall operations are performed in reverse order.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type
from deployment.steps.base_step import Step
from deployment.utils.logger import setup_logger


class Strategy(ABC):
    """
    Abstract base class for deployment strategies.

    A strategy is an ordered collection of steps that can be installed or
    uninstalled in sequence. Uninstall operations are performed in reverse order.
    """

    # Registry of all concrete strategy classes
    _strategies: List[Type['Strategy']] = []

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register concrete (non-abstract) strategy subclasses.

        This method is called when a subclass is created. It automatically
        adds concrete subclasses to the registry.
        """
        super().__init_subclass__(**kwargs)

        # Check if this is a concrete class (not abstract)
        if not getattr(cls, '__abstractmethods__', None):
            # Add to registry if not already present
            if cls not in cls._strategies:
                cls._strategies.append(cls)

    @classmethod
    def get_registered_strategies(cls) -> List[Type['Strategy']]:
        """
        Get all registered concrete strategy classes.

        Returns:
            List of concrete strategy classes
        """
        return cls._strategies.copy()

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a strategy.

        Args:
            name: Unique name for this strategy
            description: Optional description of what this strategy does
        """
        self.name = name
        self.description = description or f"Strategy: {name}"
        self.logger = setup_logger(f"strategy.{name}")
        self._steps: List[Step] = []
        self._installed = False

    @property
    def is_installed(self) -> bool:
        """Check if this strategy is currently installed."""
        return self._installed

    @property
    def steps(self) -> List[Step]:
        """Get a copy of the steps list."""
        return self._steps.copy()

    @abstractmethod
    def get_steps(self) -> List[Step]:
        """
        Get the ordered list of steps for this strategy.
        This method should be implemented by subclasses to define their steps.

        Returns:
            List of Step instances in installation order
        """
        raise NotImplementedError("Subclasses must implement get_steps method")

    def add_step(self, step: Step) -> None:
        """
        Add a step to this strategy.

        Args:
            step: Step instance to add
        """
        if step not in self._steps:
            self._steps.append(step)
            self.logger.info(
                f"Added step '{step.name}' to strategy '{self.name}'")
        else:
            self.logger.warning(
                f"Step '{step.name}' already exists in strategy '{self.name}'")

    def remove_step(self, step: Step) -> bool:
        """
        Remove a step from this strategy.

        Args:
            step: Step instance to remove

        Returns:
            bool: True if step was removed, False if not found
        """
        if step in self._steps:
            self._steps.remove(step)
            self.logger.info(
                f"Removed step '{step.name}' from strategy '{self.name}'")
            return True
        else:
            self.logger.warning(
                f"Step '{step.name}' not found in strategy '{self.name}'")
            return False

    async def install(self) -> bool:
        """
        Install all steps in this strategy in order.

        Returns:
            bool: True if all steps were installed successfully, False otherwise
        """
        self.logger.info(f"Starting installation of strategy '{self.name}'")

        # Get steps from subclass implementation
        steps = self.get_steps()
        if not steps:
            self.logger.warning(f"No steps defined for strategy '{self.name}'")
            return True

        # Validate all steps first
        for step in steps:
            if not await step.validate():
                self.logger.error(
                    f"Validation failed for step '{step.name}' in strategy '{self.name}'")
                return False

        # Install steps in order
        installed_steps = []
        for step in steps:
            self.logger.info(f"Installing step '{step.name}'")
            if await step.install():
                installed_steps.append(step)
                self.logger.info(f"Successfully installed step '{step.name}'")
            else:
                self.logger.error(f"Failed to install step '{step.name}'")
                # Rollback installed steps
                await self._rollback_installation(installed_steps)
                return False

        self._installed = True
        self.logger.info(
            f"Successfully installed strategy '{self.name}' with {len(steps)} steps")
        return True

    async def uninstall(self) -> bool:
        """
        Uninstall all steps in this strategy in reverse order.

        Returns:
            bool: True if all steps were uninstalled successfully, False otherwise
        """
        self.logger.info(f"Starting uninstallation of strategy '{self.name}'")

        # Get steps from subclass implementation
        steps = self.get_steps()
        if not steps:
            self.logger.warning(f"No steps defined for strategy '{self.name}'")
            return True

        # Uninstall steps in reverse order
        uninstalled_steps = []
        for step in reversed(steps):
            self.logger.info(f"Uninstalling step '{step.name}'")
            if await step.uninstall():
                uninstalled_steps.append(step)
                self.logger.info(
                    f"Successfully uninstalled step '{step.name}'")
            else:
                self.logger.error(f"Failed to uninstall step '{step.name}'")
                # Continue with remaining steps even if one fails
                continue

        self._installed = False
        self.logger.info(
            f"Uninstallation of strategy '{self.name}' completed. {len(uninstalled_steps)}/{len(steps)} steps uninstalled")
        return len(uninstalled_steps) == len(steps)

    async def _rollback_installation(self, installed_steps: List[Step]) -> None:
        """
        Rollback installation by uninstalling steps in reverse order.

        Args:
            installed_steps: List of steps that were successfully installed
        """
        self.logger.info(
            f"Rolling back installation of strategy '{self.name}'")
        for step in reversed(installed_steps):
            self.logger.info(f"Rolling back step '{step.name}'")
            await step.uninstall()

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this strategy.

        Returns:
            Dict containing strategy metadata
        """
        steps = self.get_steps()
        return {
            "name": self.name,
            "description": self.description,
            "installed": self._installed,
            "type": self.__class__.__name__,
            "step_count": len(steps),
            "steps": [step.get_metadata() for step in steps]
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed status of this strategy and its steps.

        Returns:
            Dict containing detailed status information
        """
        steps = self.get_steps()
        return {
            "strategy": {
                "name": self.name,
                "installed": self._installed,
                "step_count": len(steps)
            },
            "steps": [
                {
                    "name": step.name,
                    "installed": step.is_installed,
                    "type": step.__class__.__name__
                }
                for step in steps
            ]
        }

    def __str__(self) -> str:
        """String representation of the strategy."""
        status = "installed" if self._installed else "not installed"
        step_count = len(self.get_steps())
        return f"{self.__class__.__name__}({self.name}, {step_count} steps, {status})"

    def __repr__(self) -> str:
        """Detailed string representation of the strategy."""
        step_count = len(self.get_steps())
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}', steps={step_count}, installed={self._installed})"


__all__ = [
    "Strategy"
]
