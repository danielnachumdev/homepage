"""
Native frontend dependency installation step for the homepage project.

This step handles installing Node.js dependencies from package.json
for the frontend using npm.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List
from .base_step import Step
from backend.src.utils.command import AsyncCommand


class NativeFrontendDependencyInstallStep(Step):
    """
    Step that installs Node.js dependencies from package.json for the frontend.

    This step will:
    - Install: Run 'npm install' in the frontend directory
    - Uninstall: Not applicable for dependencies (they remain installed)
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 frontend_dir: Optional[str] = None,
                 name: str = "native-frontend-dependency-install",
                 description: str = "Install Node.js dependencies from package.json for frontend"):
        """
        Initialize the frontend dependency installation step.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            frontend_dir: Path to the frontend directory (defaults to 'frontend' in project root)
            name: Name for this step
            description: Description of what this step does
        """
        super().__init__(name, description)

        # Set project root - default to current working directory
        if project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)

        # Set frontend directory
        if frontend_dir is None:
            self.frontend_dir = self.project_root / "frontend"
        else:
            self.frontend_dir = Path(frontend_dir)

    async def install(self) -> bool:
        """
        Install dependencies by running 'npm install'.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting frontend dependency installation for frontend at %s", self.frontend_dir)

        # Check if frontend directory exists
        if not self.frontend_dir.exists() or not self.frontend_dir.is_dir():
            self.logger.error(
                "Frontend directory not found: %s", self.frontend_dir)
            return False

        # Check if package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            self.logger.error(
                "package.json not found in frontend directory: %s", package_json)
            return False

        self.logger.info("Found package.json: %s", package_json)

        # Create command to install dependencies
        npm_install_cmd = AsyncCommand(
            args=['npm', 'install'],
            cwd=self.frontend_dir
        )

        result = await npm_install_cmd.execute()
        return result.success

    async def uninstall(self) -> bool:
        """
        Uninstall dependencies.

        Note: This is not typically done as dependencies may be used by other projects.
        This method always returns True as it's considered a no-op.

        Returns:
            bool: Always True (no-op)
        """
        self.logger.info(
            "Frontend dependency uninstallation requested - this is a no-op operation")
        self.logger.info(
            "Dependencies will remain installed for potential future use")
        return True  # No-op, consider success

    async def validate(self) -> bool:
        """
        Validate that frontend dependencies can be installed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info(
            "Validating frontend dependency installation environment")

        # Check if frontend directory exists
        if not self.frontend_dir.exists() or not self.frontend_dir.is_dir():
            self.logger.error(
                "Frontend directory not found: %s", self.frontend_dir)
            return False

        self.logger.info("Frontend directory found: %s", self.frontend_dir)

        # Check if package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            self.logger.error(
                "package.json not found in frontend directory: %s", package_json)
            return False

        self.logger.info("package.json found: %s", package_json)

        # Check if npm is available
        npm_version_cmd = AsyncCommand.cmd("npm --version")
        result = await npm_version_cmd.execute()
        if not result.success:
            self.logger.error(
                "NPM is not available. Please ensure Node.js and npm are installed")
            return False

        self.logger.info("NPM is available: %s", result.stdout.strip())

        # Check if node_modules exists (optional but good to check)
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            self.logger.info(
                "node_modules directory found: %s", node_modules)
        else:
            self.logger.warning(
                "node_modules directory not found: %s", node_modules)

        self.logger.info(
            "Frontend dependency installation validation passed")
        return True

    async def get_metadata(self) -> dict:
        """
        Get metadata about this step including frontend-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = await super().get_metadata()

        try:
            # Check if package.json exists
            package_json = self.frontend_dir / "package.json"
            package_json_exists = package_json.exists()

            # Check if node_modules exists
            node_modules = self.frontend_dir / "node_modules"
            node_modules_exists = node_modules.exists()

            # Get npm version if available
            npm_version = "unknown"
            try:
                result = subprocess.run(
                    ['npm', '--version'],
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=True
                )
                npm_version = result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "package_json_exists": package_json_exists,
                "package_json_path": str(package_json) if package_json_exists else None,
                "node_modules_exists": node_modules_exists,
                "node_modules_path": str(node_modules) if node_modules_exists else None,
                "npm_version": npm_version
            })
        except Exception as e:
            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "error": str(e)
            })

        return metadata


__all__ = [
    "NativeFrontendDependencyInstallStep"
]
