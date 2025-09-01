"""
Native backend dependency installation step for the homepage project.

This step handles installing Python dependencies from requirements.txt
using the correct Python interpreter for the backend.
"""

import subprocess
from pathlib import Path
from typing import Optional
from .base_step import Step
from ..utils.interpreter import find_python_interpreter, get_interpreter_info
from ..utils.requirements import find_requirements_file, validate_requirements_file
from ..utils.process_manager import ProcessManager


class NativeBackendDependencyInstallStep(Step):
    """
    Step that installs Python dependencies from requirements.txt for the backend.

    This step will:
    - Install: Run 'pip install -r requirements.txt' using the correct Python interpreter
    - Uninstall: Not applicable for dependencies (they remain installed)
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 backend_dir: Optional[str] = None,
                 name: str = "native-backend-dependency-install",
                 description: str = "Install Python dependencies from requirements.txt for backend"):
        """
        Initialize the dependency installation step.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            backend_dir: Path to the backend directory (defaults to 'backend' in project root)
            name: Name for this step
            description: Description of what this step does
        """
        super().__init__(name, description)

        # Set project root - default to current working directory
        if project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)

        # Set backend directory
        if backend_dir is None:
            self.backend_dir = self.project_root / "backend"
        else:
            self.backend_dir = Path(backend_dir)

    def install(self) -> bool:
        """
        Install dependencies by running 'pip install -r requirements.txt'.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting dependency installation for backend at %s", self.backend_dir)

        try:
            # Find the correct Python interpreter
            interpreter_path = find_python_interpreter(
                self.project_root, self.backend_dir)
            self.logger.info("Using Python interpreter: %s", interpreter_path)

            # Get interpreter info
            interpreter_info = get_interpreter_info(interpreter_path)
            if not interpreter_info.working:
                self.logger.error(
                    "Python interpreter is not working: %s", interpreter_path)
                return False

            self.logger.info("Python interpreter info: %s",
                             interpreter_info.version)
            if interpreter_info.is_virtual_env:
                self.logger.info("Using virtual environment: %s",
                                 interpreter_info.executable)

            # Find requirements.txt file
            requirements_file = find_requirements_file(self.backend_dir)
            if requirements_file is None:
                self.logger.error(
                    "Requirements file not found in backend directory: %s", self.backend_dir)
                return False

            self.logger.info("Found requirements file: %s", requirements_file)

            # Validate requirements file
            validation_result = validate_requirements_file(requirements_file)
            if not validation_result.valid:
                self.logger.error(
                    "Requirements file validation failed: %s", validation_result.error)
                return False

            requirements_info = validation_result.info
            self.logger.info("Requirements file contains %d packages",
                             requirements_info.package_count)

            # Install dependencies using ProcessManager
            self.logger.info("Installing dependencies using pip...")

            result = ProcessManager.spawn(
                command=[interpreter_path, '-m', 'pip',
                         'install', '-r', str(requirements_file)],
                detached=False,
                cwd=self.backend_dir,
                log_dir=self.backend_dir / 'logs',
                log_prefix='pip_install'
            )

            if not result.success:
                self.logger.error(
                    "Failed to install backend dependencies: %s", result.error_message)
                return False

            # Wait for the process to complete
            if result.process:
                stdout, stderr = result.process.communicate()

                self.logger.info(
                    "Dependency installation completed successfully")
                self.logger.debug("Pip output: %s", stdout)

                if stderr:
                    self.logger.warning("Pip warnings: %s", stderr)

            self._mark_installed()
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Dependency installation failed with return code %d", e.returncode)
            self.logger.error("Error output: %s", e.stderr)
            if e.stdout:
                self.logger.error("Standard output: %s", e.stdout)
            return False

        except FileNotFoundError:
            self.logger.error(
                "Python interpreter not found: %s", interpreter_path)
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during dependency installation: %s", e)
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
            "Dependency uninstallation requested - this is a no-op operation")
        self.logger.info(
            "Dependencies will remain installed for potential future use")
        self._mark_uninstalled()
        return True

    def validate(self) -> bool:
        """
        Validate that dependencies can be installed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating dependency installation environment")

        try:
            # Find the correct Python interpreter
            interpreter_path = find_python_interpreter(
                self.project_root, self.backend_dir)
            self.logger.info("Found Python interpreter: %s", interpreter_path)

            # Get interpreter info
            interpreter_info = get_interpreter_info(interpreter_path)
            if not interpreter_info.working:
                self.logger.error(
                    "Python interpreter is not working: %s", interpreter_path)
                return False

            self.logger.info("Python interpreter is working: %s",
                             interpreter_info.version)

            # Check if pip is available
            try:
                result = subprocess.run(
                    [interpreter_path, '-m', 'pip', '--version'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.logger.info("Pip is available: %s", result.stdout.strip())
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error(
                    "Pip is not available with this Python interpreter")
                return False

            # Find and validate requirements file
            requirements_file = find_requirements_file(self.backend_dir)
            if requirements_file is None:
                self.logger.error(
                    "Requirements file not found in backend directory: %s", self.backend_dir)
                return False

            self.logger.info("Found requirements file: %s", requirements_file)

            # Validate requirements file
            validation_result = validate_requirements_file(requirements_file)
            if not validation_result.valid:
                self.logger.error(
                    "Requirements file validation failed: %s", validation_result.error)
                return False

            requirements_info = validation_result.info
            self.logger.info(
                "Requirements file is valid with %d packages", requirements_info.package_count)

            self.logger.info("Dependency installation validation passed")
            return True

        except Exception as e:
            self.logger.error(
                "Dependency installation validation failed: %s", e)
            return False

    def get_metadata(self) -> dict:
        """
        Get metadata about this step including dependency-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = super().get_metadata()

        try:
            # Get interpreter info
            interpreter_path = find_python_interpreter(
                self.project_root, self.backend_dir)
            interpreter_info = get_interpreter_info(interpreter_path)

            # Get requirements info
            requirements_file = find_requirements_file(self.backend_dir)
            requirements_info = None
            if requirements_file:
                validation_result = validate_requirements_file(
                    requirements_file)
                if validation_result.valid:
                    requirements_info = validation_result.info

            metadata.update({
                "project_root": str(self.project_root),
                "backend_dir": str(self.backend_dir),
                "interpreter_path": interpreter_path,
                "interpreter_working": interpreter_info.working,
                "interpreter_version": interpreter_info.version,
                "is_virtual_env": interpreter_info.is_virtual_env,
                "requirements_file": str(requirements_file) if requirements_file else None,
                "requirements_valid": requirements_info is not None,
                "package_count": requirements_info.package_count if requirements_info else 0
            })
        except Exception as e:
            metadata.update({
                "project_root": str(self.project_root),
                "backend_dir": str(self.backend_dir),
                "error": str(e)
            })

        return metadata


__all__ = [
    "NativeBackendDependencyInstallStep"
]
