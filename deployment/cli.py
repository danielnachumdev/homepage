"""
Command Line Interface for the deployment system.

This module provides a CLI class that can be used with Google Fire
to manage deployment steps and strategies.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .steps import *
from .strategies import *
from .utils import setup_logger


class DeploymentCLI:
    """
    Homepage Deployment CLI
    
    Manage deployment steps and strategies for the homepage application.
    
    Usage:
        python deploy.py step list                    # List available steps
        python deploy.py step install STEP_NAME       # Install a step
        python deploy.py step uninstall STEP_NAME     # Uninstall a step
        python deploy.py step validate STEP_NAME      # Validate a step
        python deploy.py step info STEP_NAME          # Get step information
        
        python deploy.py strategy list                # List available strategies
        python deploy.py strategy install STRATEGY    # Deploy a strategy
        python deploy.py strategy uninstall STRATEGY  # Stop a strategy
        python deploy.py strategy validate STRATEGY   # Validate a strategy
        python deploy.py strategy info STRATEGY       # Get strategy information
        
        python deploy.py info                         # Get CLI information
    """

    def __init__(self, project_root: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize the deployment CLI.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self._logger = setup_logger("deployment_cli", log_level)

        # Get dynamic registries from base classes
        self._steps_registry = self._build_steps_registry()
        self._strategies_registry = self._build_strategies_registry()

        # Initialize subcommand handlers
        self.step = self.Step(self)
        self.strategy = self.Strategy(self)

    def _build_steps_registry(self) -> Dict[str, Any]:
        """
        Build the steps registry from dynamically registered step classes.

        Returns:
            Dictionary mapping step names to step classes
        """
        from deployment.steps.base_step import Step

        registry = {}
        for step_class in Step.__subclasses__():
            name = self._class_name_to_kebab(step_class.__name__)
            registry[name] = step_class

        return registry

    def _build_strategies_registry(self) -> Dict[str, Any]:
        """
        Build the strategies registry from dynamically registered strategy classes.

        Returns:
            Dictionary mapping strategy names to strategy classes
        """
        from deployment.strategies.base_strategy import Strategy

        registry = {}
        for strategy_class in Strategy.__subclasses__():
            name = self._class_name_to_kebab(strategy_class.__name__)
            registry[name] = strategy_class

        return registry

    def _class_name_to_kebab(self, class_name: str) -> str:
        """
        Convert a class name to kebab-case.

        Args:
            class_name: The class name to convert

        Returns:
            The kebab-case version of the class name
        """
        import re
        # Insert hyphens before uppercase letters (except the first one)
        kebab = re.sub(r'(?<!^)(?=[A-Z])', '-', class_name)
        return kebab.lower()

    class Step:
        """
        Step Management Commands
        
        Manage individual deployment steps (backend, frontend, dependencies, etc.)
        
        Commands:
            list                    # List all available steps
            install STEP_NAME       # Install a specific step
            uninstall STEP_NAME     # Uninstall a specific step
            validate STEP_NAME      # Check if step is properly configured
            info STEP_NAME          # Get detailed step information
        """
        
        def __init__(self, cli_instance):
            self.cli = cli_instance

        def list(self) -> Dict[str, str]:
            """List available deployment steps."""
            steps_info = {}

            for name, step_class in self.cli._steps_registry.items():
                try:
                    # Create a temporary instance to get description
                    temp_instance = step_class(project_root=str(self.cli.project_root))
                    description = temp_instance.description
                except Exception as e:
                    description = f"Error getting description: {e}"

                steps_info[name] = description

            return steps_info

        async def install(self, step_name: str, **kwargs) -> bool:
            """Install a deployment step."""
            return await self.cli._install_step(step_name, **kwargs)

        async def uninstall(self, step_name: str, **kwargs) -> bool:
            """Uninstall a deployment step."""
            return await self.cli._uninstall_step(step_name, **kwargs)

        async def check(self, step_name: str, **kwargs) -> bool:
            """Check if a step is properly configured."""
            return await self.cli._check_step(step_name, **kwargs)

        async def info(self, step_name: str, **kwargs) -> Dict[str, Any]:
            """Get detailed information about a step."""
            return await self.cli._step_info(step_name, **kwargs)

    class Strategy:
        """
        Strategy Management Commands
        
        Manage deployment strategies (collections of steps)
        
        Commands:
            list                    # List all available strategies
            install STRATEGY_NAME   # Deploy a strategy (install all its steps)
            uninstall STRATEGY_NAME # Stop a strategy (uninstall all its steps)
            validate STRATEGY_NAME  # Check if strategy is properly configured
            info STRATEGY_NAME      # Get detailed strategy information
        """
        
        def __init__(self, cli_instance):
            self.cli = cli_instance

        def list(self) -> Dict[str, str]:
            """List available deployment strategies."""
            strategies_info = {}

            for name, strategy_class in self.cli._strategies_registry.items():
                try:
                    # Create a temporary instance to get description
                    temp_instance = strategy_class(project_root=str(self.cli.project_root))
                    description = temp_instance.description
                except Exception as e:
                    description = f"Error getting description: {e}"

                strategies_info[name] = description

            return strategies_info

        async def install(self, strategy_name: str, **kwargs) -> bool:
            """Install a strategy (deploy all its steps)."""
            return await self.cli._deploy_strategy(strategy_name, **kwargs)

        async def uninstall(self, strategy_name: str, **kwargs) -> bool:
            """Uninstall a strategy (stop all its steps)."""
            return await self.cli._stop_strategy(strategy_name, **kwargs)

        async def validate(self, strategy_name: str, **kwargs) -> bool:
            """Validate a strategy (check if all its steps are properly configured)."""
            return await self.cli._validate_strategy(strategy_name, **kwargs)

        async def info(self, strategy_name: str, **kwargs) -> Dict[str, Any]:
            """Get detailed information about a strategy."""
            return await self.cli._strategy_info(strategy_name, **kwargs)

    # Internal methods (prefixed with _ to avoid Fire conflicts)
    async def _install_step(self, step_name: str, **kwargs) -> bool:
        """
        Install a deployment step.

        Args:
            step_name: Name of the step to install
            **kwargs: Additional arguments for the step

        Returns:
            True if successful, False otherwise
        """
        self._logger.info("Installing step: %s", step_name)

        if step_name not in self._steps_registry:
            self._logger.error("Unknown step: %s", step_name)
            self._logger.info("Available steps: %s",
                              list(self._steps_registry.keys()))
            return False

        try:
            # Create step instance
            step_class = self._steps_registry[step_name]
            step = step_class(project_root=str(self.project_root), **kwargs)

            # Validate before installation
            self._logger.info("Validating step: %s", step_name)
            if not await step.validate():
                self._logger.error("Step validation failed: %s", step_name)
                return False

            # Install the step
            self._logger.info("Installing step: %s", step_name)
            success = await step.install()

            if success:
                self._logger.info("Step installed successfully: %s", step_name)
            else:
                self._logger.error("Step installation failed: %s", step_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error installing step %s: %s", step_name, e)
            return False

    async def _uninstall_step(self, step_name: str, **kwargs) -> bool:
        """
        Uninstall a deployment step.

        Args:
            step_name: Name of the step to uninstall
            **kwargs: Additional arguments for the step

        Returns:
            True if successful, False otherwise
        """
        self._logger.info("Uninstalling step: %s", step_name)

        if step_name not in self._steps_registry:
            self._logger.error("Unknown step: %s", step_name)
            self._logger.info("Available steps: %s",
                              list(self._steps_registry.keys()))
            return False

        try:
            # Create step instance
            step_class = self._steps_registry[step_name]
            step = step_class(project_root=str(self.project_root), **kwargs)

            # Uninstall the step
            self._logger.info("Uninstalling step: %s", step_name)
            success = await step.uninstall()

            if success:
                self._logger.info(
                    "Step uninstalled successfully: %s", step_name)
            else:
                self._logger.error("Step uninstallation failed: %s", step_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error uninstalling step %s: %s", step_name, e)
            return False

    async def _deploy_strategy(self, strategy_name: str, **kwargs) -> bool:
        """
        Deploy a strategy (install all its steps).

        Args:
            strategy_name: Name of the strategy to deploy
            **kwargs: Additional arguments for the strategy

        Returns:
            True if successful, False otherwise
        """
        self._logger.info("Installing strategy: %s", strategy_name)

        if strategy_name not in self._strategies_registry:
            self._logger.error("Unknown strategy: %s", strategy_name)
            self._logger.info("Available strategies: %s",
                              list(self._strategies_registry.keys()))
            return False

        try:
            # Create strategy instance
            strategy_class = self._strategies_registry[strategy_name]
            strategy = strategy_class(
                project_root=str(self.project_root), **kwargs)

            # Install the strategy
            self._logger.info("Installing strategy: %s", strategy_name)
            success = await strategy.install()

            if success:
                self._logger.info(
                    "Strategy installed successfully: %s", strategy_name)
            else:
                self._logger.error(
                    "Strategy installation failed: %s", strategy_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error installing strategy %s: %s", strategy_name, e)
            return False

    async def _stop_strategy(self, strategy_name: str, **kwargs) -> bool:
        """
        Stop a strategy (uninstall all its steps).

        Args:
            strategy_name: Name of the strategy to stop
            **kwargs: Additional arguments for the strategy

        Returns:
            True if successful, False otherwise
        """
        self._logger.info("Uninstalling strategy: %s", strategy_name)

        if strategy_name not in self._strategies_registry:
            self._logger.error("Unknown strategy: %s", strategy_name)
            self._logger.info("Available strategies: %s",
                              list(self._strategies_registry.keys()))
            return False

        try:
            # Create strategy instance
            strategy_class = self._strategies_registry[strategy_name]
            strategy = strategy_class(
                project_root=str(self.project_root), **kwargs)

            # Uninstall the strategy
            self._logger.info("Uninstalling strategy: %s", strategy_name)
            success = await strategy.uninstall()

            if success:
                self._logger.info(
                    "Strategy uninstalled successfully: %s", strategy_name)
            else:
                self._logger.error(
                    "Strategy uninstallation failed: %s", strategy_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error uninstalling strategy %s: %s", strategy_name, e)
            return False

    async def _check_step(self, step_name: str, **kwargs) -> bool:
        """
        Check if a step is properly configured.

        Args:
            step_name: Name of the step to check
            **kwargs: Additional arguments for the step

        Returns:
            True if valid, False otherwise
        """
        self._logger.info("Validating step: %s", step_name)

        if step_name not in self._steps_registry:
            self._logger.error("Unknown step: %s", step_name)
            self._logger.info("Available steps: %s",
                              list(self._steps_registry.keys()))
            return False

        try:
            # Create step instance
            step_class = self._steps_registry[step_name]
            step = step_class(project_root=str(self.project_root), **kwargs)

            # Validate the step
            success = await step.validate()

            if success:
                self._logger.info("Step validation passed: %s", step_name)
            else:
                self._logger.error("Step validation failed: %s", step_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error validating step %s: %s", step_name, e)
            return False

    async def _step_info(self, step_name: str, **kwargs) -> Dict[str, Any]:
        """
        Get metadata for a deployment step by name.

        Args:
            step_name: Name of the step to get metadata for
            **kwargs: Additional arguments to pass to the step constructor

        Returns:
            Dictionary containing step metadata
        """
        if step_name not in self._steps_registry:
            self._logger.error("Unknown step: %s", step_name)
            self._logger.info("Available steps: %s",
                              list(self._steps_registry.keys()))
            return {}

        try:
            # Create step instance
            step_class = self._steps_registry[step_name]
            step = step_class(project_root=str(self.project_root), **kwargs)

            # Get metadata
            metadata = await step.get_metadata()

            return metadata

        except Exception as e:
            self._logger.error(
                "Unexpected error getting step metadata %s: %s", step_name, e)
            return {}

    async def _validate_strategy(self, strategy_name: str, **kwargs) -> bool:
        """
        Validate a strategy (check if all its steps are properly configured).

        Args:
            strategy_name: Name of the strategy to validate
            **kwargs: Additional arguments for the strategy

        Returns:
            True if valid, False otherwise
        """
        self._logger.info("Validating strategy: %s", strategy_name)

        if strategy_name not in self._strategies_registry:
            self._logger.error("Unknown strategy: %s", strategy_name)
            self._logger.info("Available strategies: %s",
                              list(self._strategies_registry.keys()))
            return False

        try:
            # Create strategy instance
            strategy_class = self._strategies_registry[strategy_name]
            strategy = strategy_class(project_root=str(self.project_root), **kwargs)

            # Get all steps and validate each one
            steps = strategy.get_steps()
            all_valid = True

            for step in steps:
                step_name = self._class_name_to_kebab(step.__class__.__name__)
                self._logger.info("Validating step: %s", step_name)
                
                if not await step.validate():
                    self._logger.error("Step validation failed: %s", step_name)
                    all_valid = False
                else:
                    self._logger.info("Step validation passed: %s", step_name)

            if all_valid:
                self._logger.info("Strategy validation passed: %s", strategy_name)
            else:
                self._logger.error("Strategy validation failed: %s", strategy_name)

            return all_valid

        except Exception as e:
            self._logger.error(
                "Unexpected error validating strategy %s: %s", strategy_name, e)
            return False

    async def _strategy_info(self, strategy_name: str, **kwargs) -> Dict[str, Any]:
        """
        Get metadata for a deployment strategy by name.

        Args:
            strategy_name: Name of the strategy to get metadata for
            **kwargs: Additional arguments to pass to the strategy constructor

        Returns:
            Dictionary containing strategy metadata
        """
        if strategy_name not in self._strategies_registry:
            self._logger.error("Unknown strategy: %s", strategy_name)
            self._logger.info("Available strategies: %s",
                              list(self._strategies_registry.keys()))
            return {}

        try:
            # Create strategy instance
            strategy_class = self._strategies_registry[strategy_name]
            strategy = strategy_class(project_root=str(self.project_root), **kwargs)

            # Get metadata
            metadata = await strategy.get_metadata()

            return metadata

        except Exception as e:
            self._logger.error(
                "Unexpected error getting strategy metadata %s: %s", strategy_name, e)
            return {}

    def info(self) -> Dict[str, Any]:
        """
        Get general information about the deployment CLI.

        Returns:
            Dictionary containing CLI information
        """
        return {
            "project_root": str(self.project_root),
            "available_steps": list(self._steps_registry.keys()),
            "available_strategies": list(self._strategies_registry.keys()),
            "steps_count": len(self._steps_registry),
            "strategies_count": len(self._strategies_registry)
        }


def main():
    """
    Main entry point for when the CLI module is executed directly.

    Uses Google Fire to create a CLI from the DeploymentCLI class.
    """
    try:
        import fire
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure you have installed the required dependencies:")
        print("  pip install fire")
        sys.exit(1)

    try:
        # Create CLI instance and use Fire to generate the command-line interface
        cli = DeploymentCLI()
        fire.Fire(cli)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


__all__ = [
    "DeploymentCLI"
]