"""
Native frontend deployment step for the homepage project.

This step handles deploying the frontend using npm run dev
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


class NativeFrontendDeployStep(Step):
    """
    Step that deploys the frontend application using npm run dev
    and native system resources.

    This step will:
    - Install: Start the frontend development server by running 'npm run dev' in the frontend directory
    - Uninstall: Stop the frontend development server process
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 frontend_dir: Optional[str] = None,
                 name: str = "native-frontend-deploy",
                 description: str = "Deploy frontend using npm run dev and native system resources"):
        """
        Initialize the frontend deployment step.

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

        # Store the process reference for uninstallation
        self._process: Optional[subprocess.Popen] = None

        self.logger.info("NativeFrontendDeployStep initialized with project_root=%s, frontend_dir=%s",
                         self.project_root, self.frontend_dir)

    def install(self) -> bool:
        """
        Install the frontend by starting the development server process.

        Runs 'npm run dev' in the frontend directory.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting frontend deployment in directory %s", self.frontend_dir)

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
                    "Frontend package.json not found: %s", package_json)
                return False

            # Check if we already have a running process
            if self._process is not None and self._process.poll() is None:
                self.logger.warning(
                    "Frontend process is already running (PID: %d)", self._process.pid)
                self._mark_installed()
                return True

            # Start the frontend process
            self.logger.info("Starting frontend process: npm run dev")

            self._process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Give the process a moment to start
            time.sleep(2)

            # Check if the process is still running
            if self._process.poll() is not None:
                # Process exited immediately, something went wrong
                stdout, stderr = self._process.communicate()
                self.logger.error(
                    "Frontend process exited immediately with code %d", self._process.returncode)
                if stdout:
                    self.logger.error("Frontend stdout: %s", stdout)
                if stderr:
                    self.logger.error("Frontend stderr: %s", stderr)
                self._process = None
                return False

            self.logger.info(
                "Frontend process started successfully (PID: %d)", self._process.pid)
            self._mark_installed()
            return True

        except FileNotFoundError:
            self.logger.error(
                "NPM command not found. Please ensure Node.js and npm are installed")
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during frontend deployment: %s", e)
            if self._process:
                self._process = None
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the frontend by stopping the development server process.

        Terminates the running frontend process.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Stopping frontend deployment")

        try:
            if self._process is None:
                self.logger.warning("No frontend process to stop")
                self._mark_uninstalled()
                return True

            # Check if process is still running
            if self._process.poll() is not None:
                self.logger.info("Frontend process already stopped")
                self._process = None
                self._mark_uninstalled()
                return True

            # Terminate the process gracefully first
            self.logger.info(
                "Terminating frontend process (PID: %d)", self._process.pid)
            self._process.terminate()

            # Wait for graceful shutdown
            try:
                self._process.wait(timeout=10)
                self.logger.info("Frontend process terminated gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination failed
                self.logger.warning(
                    "Frontend process did not terminate gracefully, forcing kill")
                self._process.kill()
                self._process.wait()
                self.logger.info("Frontend process killed")

            self._process = None
            self._mark_uninstalled()
            return True

        except Exception as e:
            self.logger.error(
                "Unexpected error during frontend uninstallation: %s", e)
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
        Validate that the frontend can be deployed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating frontend deployment environment")

        # Check if npm is available
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("NPM is available: %s", result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error(
                "NPM is not available. Please ensure Node.js and npm are installed")
            return False

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
                "Frontend package.json not found: %s", package_json)
            return False

        self.logger.info("Frontend package.json found: %s", package_json)

        # Check if node_modules exists (optional but good to check)
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            self.logger.info("Frontend node_modules found: %s", node_modules)
        else:
            self.logger.warning(
                "Frontend node_modules not found: %s", node_modules)

        # Check if package.json has a dev script
        try:
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            scripts = package_data.get('scripts', {})
            if 'dev' not in scripts:
                self.logger.error("No 'dev' script found in package.json")
                return False

            self.logger.info("Frontend 'dev' script found: %s", scripts['dev'])
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error("Failed to read package.json: %s", e)
            return False

        self.logger.info("Frontend deployment validation passed")
        return True

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
                    check=True
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
                "npm_version": npm_version,
                "process_running": self._process is not None and self._process.poll() is None,
                "process_pid": self._process.pid if self._process else None
            })
        except Exception as e:
            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "process_running": self._process is not None and self._process.poll() is None,
                "process_pid": self._process.pid if self._process else None,
                "error": str(e)
            })
        return metadata

    def is_process_running(self) -> bool:
        """
        Check if the frontend process is currently running.

        Returns:
            bool: True if process is running, False otherwise
        """
        if self._process is None:
            return False
        return self._process.poll() is None

    def get_process_info(self) -> dict:
        """
        Get information about the current frontend process.

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
    "NativeFrontendDeployStep"
]
