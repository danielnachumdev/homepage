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
from deployment.utils.interpreter import find_python_interpreter, get_interpreter_info


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

        # Note: We don't store process references as they won't persist between invocations

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

            # Check if backend is already running
            from deployment.utils import is_backend_running
            backend_status = is_backend_running(
                str(self.project_root), str(self.backend_dir))
            if backend_status.found:
                self.logger.warning(
                    "Backend is already running, skipping startup")
                self.logger.info("Found %d backend process(es)",
                                 backend_status.total_count)
                for proc in backend_status.processes:
                    self.logger.info("  - PID %d: %s", proc.pid,
                                     ' '.join(proc.cmdline))
                self._mark_installed()
                return True

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

            # Start the backend process
            self.logger.info("Starting backend process: %s %s",
                             interpreter_path, main_file)

            process = subprocess.Popen(
                [interpreter_path, str(main_file)],
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
            if process.poll() is not None:
                # Process exited immediately, something went wrong
                stdout, stderr = process.communicate()
                self.logger.error(
                    "Backend process exited immediately with code %d", process.returncode)
                if stdout:
                    self.logger.error("Backend stdout: %s", stdout)
                if stderr:
                    self.logger.error("Backend stderr: %s", stderr)
                return False

            self.logger.info(
                "Backend process started successfully (PID: %d)", process.pid)
            self._mark_installed()
            return True

        except FileNotFoundError:
            self.logger.error(
                "Python interpreter not found: %s", interpreter_path)
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during backend deployment: %s", e)
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the backend by stopping the server process.

        Finds and terminates running backend processes.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Stopping backend deployment")

        try:
            # Find running backend processes
            from deployment.utils import is_backend_running, kill_process
            backend_status = is_backend_running(
                str(self.project_root), str(self.backend_dir))

            if not backend_status.found:
                self.logger.info("No backend processes found to stop")
                self._mark_uninstalled()
                return True

            self.logger.info(
                "Found %d backend process(es) to stop", backend_status.total_count)

            # Terminate all found processes
            success_count = 0
            for proc in backend_status.processes:
                self.logger.info(
                    "Terminating backend process (PID: %d)", proc.pid)
                if kill_process(proc.pid, timeout=10):
                    self.logger.info(
                        "Backend process %d terminated successfully", proc.pid)
                    success_count += 1
                else:
                    self.logger.warning(
                        "Failed to terminate backend process %d", proc.pid)

            if success_count == backend_status.total_count:
                self.logger.info("All backend processes stopped successfully")
                self._mark_uninstalled()
                return True
            else:
                self.logger.warning(
                    "Some backend processes could not be stopped")
                self._mark_uninstalled()
                return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during backend uninstallation: %s", e)
            return False

    def validate(self) -> bool:
        """
        Validate that the backend can be deployed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating backend deployment environment")

        # Find and validate the correct Python interpreter
        try:
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
            if interpreter_info.is_virtual_env:
                self.logger.info("Using virtual environment: %s",
                                 interpreter_info.executable)

        except Exception as e:
            self.logger.error("Failed to find Python interpreter: %s", e)
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
        try:
            # Get interpreter info
            interpreter_path = find_python_interpreter(
                self.project_root, self.backend_dir)
            interpreter_info = get_interpreter_info(interpreter_path)

            metadata.update({
                "project_root": str(self.project_root),
                "backend_dir": str(self.backend_dir),
                "interpreter_path": interpreter_path,
                "interpreter_working": interpreter_info.working,
                "interpreter_version": interpreter_info.version,
                "is_virtual_env": interpreter_info.is_virtual_env,
                "backend_dir_exists": self.backend_dir.exists(),
                "main_file_exists": (self.backend_dir / "__main__.py").exists()
            })
        except Exception as e:
            metadata.update({
                "project_root": str(self.project_root),
                "backend_dir": str(self.backend_dir),
                "python_executable": sys.executable,  # fallback
                "backend_dir_exists": self.backend_dir.exists(),
                "main_file_exists": (self.backend_dir / "__main__.py").exists(),
                "error": str(e)
            })
        return metadata

    def is_process_running(self) -> bool:
        """
        Check if the backend process is currently running.

        Returns:
            bool: True if process is running, False otherwise
        """
        from deployment.utils import is_backend_running
        backend_status = is_backend_running(
            str(self.project_root), str(self.backend_dir))
        return backend_status.found

    def get_process_info(self) -> dict:
        """
        Get information about the current backend process.

        Returns:
            Dict containing process information
        """
        from deployment.utils import is_backend_running
        backend_status = is_backend_running(
            str(self.project_root), str(self.backend_dir))

        if not backend_status.found:
            return {"status": "not_running", "process_count": 0}

        processes_info = []
        for proc in backend_status.processes:
            processes_info.append({
                "pid": proc.pid,
                "name": proc.name,
                "cmdline": proc.cmdline,
                "cwd": proc.cwd,
                "status": proc.status
            })

        return {
            "status": "running",
            "process_count": backend_status.total_count,
            "processes": processes_info
        }


__all__ = [
    "NativeBackendDeployStep"
]
