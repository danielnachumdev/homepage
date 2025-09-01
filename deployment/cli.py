"""
Command Line Interface for the deployment system.

This module provides a CLI class that can be used with Google Fire
to manage deployment steps and strategies.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from deployment.utils import setup_logger
from deployment.steps import (
    DockerDeployStep, NativeBackendDeployStep, NativeBackendDependencyInstallStep,
    NativeFrontendDeployStep, NativeFrontendDependencyInstallStep, WindowsStartOnLoginStep
)
from deployment.strategies import DockerDeployStrategy


class DeploymentCLI:
    """
    Command Line Interface for deployment operations.

    This class provides methods to install/uninstall steps and strategies
    with proper logging and error handling.
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

        # Available steps registry
        self._steps_registry = {
            "docker-deploy": DockerDeployStep,
            "native-backend-deploy": NativeBackendDeployStep,
            "native-backend-dependency-install": NativeBackendDependencyInstallStep,
            "native-frontend-deploy": NativeFrontendDeployStep,
            "native-frontend-dependency-install": NativeFrontendDependencyInstallStep,
            "windows-start-on-login": WindowsStartOnLoginStep,
        }

        # Available strategies registry
        self._strategies_registry = {
            "docker-deploy": DockerDeployStrategy,
        }

    def list_steps(self) -> Dict[str, str]:
        """
        List all available deployment steps.

        Returns:
            Dictionary mapping step names to their descriptions
        """
        steps_info = {}

        for name, step_class in self._steps_registry.items():
            # Create a temporary instance to get description
            try:
                temp_step = step_class(project_root=str(self.project_root))
                description = temp_step.description
            except Exception as e:
                description = f"Error creating step: {e}"

            steps_info[name] = description

        return steps_info

    def list_strategies(self) -> Dict[str, str]:
        """
        List all available deployment strategies.

        Returns:
            Dictionary mapping strategy names to their descriptions
        """
        strategies_info = {}

        for name, strategy_class in self._strategies_registry.items():
            # Create a temporary instance to get description
            try:
                temp_strategy = strategy_class(
                    project_root=str(self.project_root))
                description = temp_strategy.description
            except Exception as e:
                description = f"Error creating strategy: {e}"

            strategies_info[name] = description

        return strategies_info

    def install_step(self, step_name: str, **kwargs) -> bool:
        """
        Install a deployment step by name.

        Args:
            step_name: Name of the step to install
            **kwargs: Additional arguments to pass to the step constructor

        Returns:
            True if installation was successful, False otherwise
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
            if not step.validate():
                self._logger.error("Step validation failed: %s", step_name)
                return False

            # Install the step
            self._logger.info("Installing step: %s", step_name)
            success = step.install()

            if success:
                self._logger.info("Step installed successfully: %s", step_name)
            else:
                self._logger.error("Step installation failed: %s", step_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error installing step %s: %s", step_name, e)
            return False

    def uninstall_step(self, step_name: str, **kwargs) -> bool:
        """
        Uninstall a deployment step by name.

        Args:
            step_name: Name of the step to uninstall
            **kwargs: Additional arguments to pass to the step constructor

        Returns:
            True if uninstallation was successful, False otherwise
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
            success = step.uninstall()

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

    def install_strategy(self, strategy_name: str, **kwargs) -> bool:
        """
        Install a deployment strategy by name.

        Args:
            strategy_name: Name of the strategy to install
            **kwargs: Additional arguments to pass to the strategy constructor

        Returns:
            True if installation was successful, False otherwise
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
            success = strategy.install()

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

    def uninstall_strategy(self, strategy_name: str, **kwargs) -> bool:
        """
        Uninstall a deployment strategy by name.

        Args:
            strategy_name: Name of the strategy to uninstall
            **kwargs: Additional arguments to pass to the strategy constructor

        Returns:
            True if uninstallation was successful, False otherwise
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
            success = strategy.uninstall()

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

    def validate_step(self, step_name: str, **kwargs) -> bool:
        """
        Validate a deployment step by name.

        Args:
            step_name: Name of the step to validate
            **kwargs: Additional arguments to pass to the step constructor

        Returns:
            True if validation passed, False otherwise
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
            success = step.validate()

            if success:
                self._logger.info("Step validation passed: %s", step_name)
            else:
                self._logger.error("Step validation failed: %s", step_name)

            return success

        except Exception as e:
            self._logger.error(
                "Unexpected error validating step %s: %s", step_name, e)
            return False

    def get_step_metadata(self, step_name: str, **kwargs) -> Dict[str, Any]:
        """
        Get metadata for a deployment step by name.

        Args:
            step_name: Name of the step to get metadata for
            **kwargs: Additional arguments to pass to the step constructor

        Returns:
            Dictionary containing step metadata
        """
        self._logger.info("Getting metadata for step: %s", step_name)

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
            metadata = step.get_metadata()

            self._logger.info("Step metadata retrieved for: %s", step_name)
            for key, value in metadata.items():
                self._logger.info("  %s: %s", key, value)

            return metadata

        except Exception as e:
            self._logger.error(
                "Unexpected error getting metadata for step %s: %s", step_name, e)
            return {}

    def info(self) -> Dict[str, Any]:
        """
        Get information about the deployment system.

        Returns:
            Dictionary containing system information
        """
        self._logger.info("Deployment System Information")
        self._logger.info("Project Root: %s", self.project_root)
        self._logger.info("Available Steps: %s",
                          list(self._steps_registry.keys()))
        self._logger.info("Available Strategies: %s",
                          list(self._strategies_registry.keys()))

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
