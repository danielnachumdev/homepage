"""
Native backend deployment step for the homepage project.

This step handles deploying the backend using the current Python interpreter
and native system resources (not containerized).
"""

import sys
import time
from pathlib import Path
from typing import Optional, List
from .base_step import Step
from backend.src.utils.command import AsyncCommand
from ..utils.interpreter import find_python_interpreter, get_interpreter_info


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

    async def install(self) -> bool:
        """
        Install the backend by starting the server process.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting backend deployment in directory %s", self.backend_dir)

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
        from ..utils.process_checker import is_backend_running
        backend_status = await is_backend_running(
            str(self.project_root), str(self.backend_dir))
        if backend_status.found:
            self.logger.warning(
                "Backend is already running, skipping startup")
            self.logger.info("Found %d backend process(es)",
                             backend_status.total_count)
            for proc in backend_status.processes:
                self.logger.info("  - PID %d: %s", proc.pid,
                                 ' '.join(proc.cmdline))
            return True  # Already running, consider success

        # Find the correct Python interpreter
        interpreter_path = await find_python_interpreter(
            self.project_root, self.backend_dir)
        self.logger.info("Using Python interpreter: %s", interpreter_path)

        # Get interpreter info
        interpreter_info = await get_interpreter_info(interpreter_path)
        if not interpreter_info.working:
            self.logger.error(
                "Python interpreter is not working: %s", interpreter_path)
            return False

        self.logger.info("Python interpreter info: %s",
                         interpreter_info.version)
        if interpreter_info.is_virtual_env:
            self.logger.info("Using virtual environment: %s",
                             interpreter_info.executable)

        # Create command to start the backend process
        backend_cmd = AsyncCommand(
            args=[interpreter_path, str(main_file)],
            cwd=self.backend_dir
        )

        result = await backend_cmd.execute()
        return result.success

    async def uninstall(self) -> bool:
        """
        Uninstall the backend by stopping the server process.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Stopping backend deployment")

        # Find running backend processes
        from ..utils.process_checker import is_backend_running
        backend_status = await is_backend_running(
            str(self.project_root), str(self.backend_dir))

        if not backend_status.found:
            self.logger.info("No backend processes found to stop")
            return True  # No processes to stop, consider success

        self.logger.info(
            "Found %d backend process(es) to stop", backend_status.total_count)

        # Use the careful process killing function
        from ..utils.process_checker import kill_processes_carefully
        return await kill_processes_carefully(
            backend_status.processes, 
            str(self.project_root), 
            str(self.backend_dir),
            str(self.project_root / "frontend"),  # frontend_dir for validation
            self.logger
        )

    async def validate(self) -> bool:
        """
        Validate that the backend can be deployed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating backend deployment environment")

        # Find and validate the correct Python interpreter
        try:
            interpreter_path = await find_python_interpreter(
                self.project_root, self.backend_dir)
            self.logger.info("Found Python interpreter: %s", interpreter_path)

            # Get interpreter info
            interpreter_info = await get_interpreter_info(interpreter_path)
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

        # Test Python syntax by running a syntax check
        syntax_check_cmd = AsyncCommand(
            args=[interpreter_path, "-m", "py_compile", str(main_file)],
            cwd=self.backend_dir
        )
        result = await syntax_check_cmd.execute()
        if not result.success:
            self.logger.error("Backend module has syntax errors: %s", result.stderr)
            return False

        self.logger.info("Backend deployment validation passed")
        return True

    async def get_metadata(self) -> dict:
        """
        Get metadata about this step including backend-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = await super().get_metadata()
        try:
            # Get interpreter info
            interpreter_path = await find_python_interpreter(self.project_root, self.backend_dir)
            interpreter_info = await get_interpreter_info(interpreter_path)

            # Check for log files
            log_dir = self.backend_dir / 'logs'
            stdout_log = log_dir / 'backend_stdout.log'
            stderr_log = log_dir / 'backend_stderr.log'

            metadata.update({
                "project_root": str(self.project_root),
                "backend_dir": str(self.backend_dir),
                "interpreter_path": interpreter_path,
                "interpreter_working": interpreter_info.working,
                "interpreter_version": interpreter_info.version,
                "is_virtual_env": interpreter_info.is_virtual_env,
                "backend_dir_exists": self.backend_dir.exists(),
                "main_file_exists": (self.backend_dir / "__main__.py").exists(),
                "log_directory": str(log_dir),
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
                "stdout_log_exists": stdout_log.exists(),
                "stderr_log_exists": stderr_log.exists()
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

    async def is_process_running(self) -> bool:
        """
        Check if the backend process is currently running.

        Returns:
            bool: True if process is running, False otherwise
        """
        from ..utils.process_checker import is_backend_running
        backend_status = await is_backend_running(
            str(self.project_root), str(self.backend_dir))
        return backend_status.found

    async def get_process_info(self) -> dict:
        """
        Get information about the current backend process.

        Returns:
            Dict containing process information
        """
        from ..utils.process_checker import is_backend_running
        backend_status = await is_backend_running(
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
