"""
Native backend deployment step for the homepage project.

This step handles deploying the backend using the current Python interpreter
and native system resources (not containerized).
"""

import os
import sys
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional
from deployment.steps.base_step import Step


class NativeBackendDeployStep(Step):
    """
    Step that deploys the backend application using the current Python interpreter
    and native system resources.

    This step will:
    - Install: Start the backend server by running 'python __main__.py' in the backend directory
    - Uninstall: Stop the backend server process
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 backend_dir: Optional[str] = None,
                 name: str = "native-backend-deploy",
                 description: str = "Deploy backend using current Python interpreter and native system resources"):
        """
        Initialize the backend deployment step.

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

        # Store the process reference for uninstallation
        self._process: Optional[subprocess.Popen] = None

        self.logger.info("NativeBackendDeployStep initialized with project_root=%s, backend_dir=%s",
                         self.project_root, self.backend_dir)

    def install(self) -> bool:
        """
        Install the backend by starting the server process.

        Runs 'python __main__.py' in the backend directory using the current interpreter.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting backend deployment in directory %s", self.backend_dir)

        try:
            # Check if backend directory exists
            if not self.backend_dir.exists() or not self.backend_dir.is_dir():
                self.logger.error(
                    "Backend directory not found: %s", self.backend_dir)
                return False

            # Check if __main__.py exists
            main_file = self.backend_dir / "__main__.py"
            if not main_file.exists():
                self.logger.error(
                    "Backend __main__.py not found: %s", main_file)
                return False

            # Check if we already have a running process
            if self._process is not None and self._process.poll() is None:
                self.logger.warning(
                    "Backend process is already running (PID: %d)", self._process.pid)
                self._mark_installed()
                return True

            # Start the backend process
            self.logger.info("Starting backend process: %s %s",
                             sys.executable, main_file)

            self._process = subprocess.Popen(
                [sys.executable, str(main_file)],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Give the process a moment to start
            time.sleep(1)

            # Check if the process is still running
            if self._process.poll() is not None:
                # Process exited immediately, something went wrong
                stdout, stderr = self._process.communicate()
                self.logger.error(
                    "Backend process exited immediately with code %d", self._process.returncode)
                if stdout:
                    self.logger.error("Backend stdout: %s", stdout)
                if stderr:
                    self.logger.error("Backend stderr: %s", stderr)
                self._process = None
                return False

            self.logger.info(
                "Backend process started successfully (PID: %d)", self._process.pid)
            self._mark_installed()
            return True

        except FileNotFoundError:
            self.logger.error(
                "Python interpreter not found: %s", sys.executable)
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during backend deployment: %s", e)
            if self._process:
                self._process = None
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the backend by stopping the server process.

        Terminates the running backend process.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Stopping backend deployment")

        try:
            if self._process is None:
                self.logger.warning("No backend process to stop")
                self._mark_uninstalled()
                return True

            # Check if process is still running
            if self._process.poll() is not None:
                self.logger.info("Backend process already stopped")
                self._process = None
                self._mark_uninstalled()
                return True

            # Terminate the process gracefully first
            self.logger.info(
                "Terminating backend process (PID: %d)", self._process.pid)
            self._process.terminate()

            # Wait for graceful shutdown
            try:
                self._process.wait(timeout=10)
                self.logger.info("Backend process terminated gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination failed
                self.logger.warning(
                    "Backend process did not terminate gracefully, forcing kill")
                self._process.kill()
                self._process.wait()
                self.logger.info("Backend process killed")

            self._process = None
            self._mark_uninstalled()
            return True

        except Exception as e:
            self.logger.error(
                "Unexpected error during backend uninstallation: %s", e)
            # Try to clean up the process reference even if there was an error
            if self._process:
                try:
                    self._process.kill()
                except:
                    pass
                self._process = None
            return False

    def validate(self) -> bool:
        """
        Validate that the backend can be deployed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating backend deployment environment")

        # Check if Python interpreter is available
        try:
            result = subprocess.run(
                [sys.executable, '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("Python interpreter found: %s",
                             result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error(
                "Python interpreter is not available or not working properly")
            return False

        # Check if backend directory exists
        if not self.backend_dir.exists() or not self.backend_dir.is_dir():
            self.logger.error(
                "Backend directory not found: %s", self.backend_dir)
            return False

        self.logger.info("Backend directory found: %s", self.backend_dir)

        # Check if __main__.py exists
        main_file = self.backend_dir / "__main__.py"
        if not main_file.exists():
            self.logger.error("Backend __main__.py not found: %s", main_file)
            return False

        self.logger.info("Backend __main__.py found: %s", main_file)

        # Check if requirements.txt exists (optional but good to check)
        requirements_file = self.backend_dir / "requirements.txt"
        if requirements_file.exists():
            self.logger.info(
                "Backend requirements.txt found: %s", requirements_file)
        else:
            self.logger.warning(
                "Backend requirements.txt not found: %s", requirements_file)

        # Try to import the backend module to check for basic syntax errors
        try:
            # Add backend directory to Python path temporarily
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.backend_dir))

            # Try to import the main module
            import __main__ as backend_main
            self.logger.info("Backend module imports successfully")

            # Restore original path
            sys.path = original_path

        except Exception as e:
            self.logger.error("Backend module has import errors: %s", e)
            return False

        self.logger.info("Backend deployment validation passed")
        return True

    def get_metadata(self) -> dict:
        """
        Get metadata about this step including backend-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = super().get_metadata()
        metadata.update({
            "project_root": str(self.project_root),
            "backend_dir": str(self.backend_dir),
            "python_executable": sys.executable,
            "backend_dir_exists": self.backend_dir.exists(),
            "main_file_exists": (self.backend_dir / "__main__.py").exists(),
            "process_running": self._process is not None and self._process.poll() is None,
            "process_pid": self._process.pid if self._process else None
        })
        return metadata

    def is_process_running(self) -> bool:
        """
        Check if the backend process is currently running.

        Returns:
            bool: True if process is running, False otherwise
        """
        if self._process is None:
            return False
        return self._process.poll() is None

    def get_process_info(self) -> dict:
        """
        Get information about the current backend process.

        Returns:
            Dict containing process information
        """
        if self._process is None:
            return {"status": "not_started"}

        if self._process.poll() is None:
            return {
                "status": "running",
                "pid": self._process.pid
            }
        else:
            return {
                "status": "stopped",
                "return_code": self._process.returncode
            }


__all__ = [
    "NativeBackendDeployStep"
]
