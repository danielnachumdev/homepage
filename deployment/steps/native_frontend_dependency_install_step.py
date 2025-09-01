"""
Native frontend dependency installation step for the homepage project.

This step handles installing Node.js dependencies from package.json
for the frontend using npm.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional
from deployment.steps.base_step import Step
from deployment.utils.process_manager import ProcessManager


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

    def install(self) -> bool:
        """
        Install dependencies by running 'npm install'.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting frontend dependency installation for frontend at %s", self.frontend_dir)

        try:
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

            # Install dependencies using ProcessManager
            self.logger.info("Installing frontend dependencies using npm...")

            result = ProcessManager.spawn(
                command=['npm', 'install'],
                detached=False,
                cwd=self.frontend_dir,
                log_dir=self.frontend_dir / 'logs',
                log_prefix='npm_install'
            )

            if not result.success:
                self.logger.error(
                    "Failed to install frontend dependencies: %s", result.error_message)
                return False

            # Wait for the process to complete
            if result.process:
                stdout, stderr = result.process.communicate()

                self.logger.info(
                    "Frontend dependency installation completed successfully")
                self.logger.debug("NPM output: %s", stdout)

                if stderr:
                    self.logger.warning("NPM warnings: %s", stderr)

            self._mark_installed()
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Frontend dependency installation failed with return code %d", e.returncode)
            self.logger.error("Error output: %s", e.stderr)
            if e.stdout:
                self.logger.error("Standard output: %s", e.stdout)
            return False

        except FileNotFoundError:
            self.logger.error(
                "NPM command not found. Please ensure Node.js and npm are installed")
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during frontend dependency installation: %s", e)
            return False

    def uninstall(self) -> bool:
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
        self._mark_uninstalled()
        return True

    def validate(self) -> bool:
        """
        Validate that frontend dependencies can be installed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info(
            "Validating frontend dependency installation environment")

        try:
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

            # Check if npm is available using ProcessManager
            try:
                result = ProcessManager.spawn(
                    command=['npm', '--version'],
                    detached=False
                )

                if not result.success or not result.process:
                    self.logger.error(
                        "NPM is not available. Please ensure Node.js and npm are installed")
                    return False

                stdout, stderr = result.process.communicate()
                self.logger.info("NPM is available: %s", stdout.strip())
            except Exception:
                self.logger.error(
                    "NPM is not available. Please ensure Node.js and npm are installed")
                return False

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

        except Exception as e:
            self.logger.error(
                "Frontend dependency installation validation failed: %s", e)
            return False

    def get_metadata(self) -> dict:
        """
        Get metadata about this step including frontend-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = super().get_metadata()

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
