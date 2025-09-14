"""
Native frontend deployment step for the homepage project.

This step handles deploying the frontend using npm run dev
and native system resources (not containerized).
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List
from deployment.steps.base_step import Step
from backend.src.utils.command import AsyncCommand


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

        # Note: We don't store process references as they won't persist between invocations

    async def install(self) -> bool:
        """
        Install the frontend by starting the development server process.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info(
            "Starting frontend deployment in directory %s", self.frontend_dir)

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

        # Check if frontend is already running
        from deployment.utils import is_frontend_running
        frontend_status = await is_frontend_running(
            str(self.project_root), str(self.frontend_dir))
        if frontend_status.found:
            self.logger.warning(
                "Frontend is already running, skipping startup")
            self.logger.info("Found %d frontend process(es)",
                             frontend_status.total_count)
            for proc in frontend_status.processes:
                self.logger.info("  - PID %d: %s", proc.pid,
                                 ' '.join(proc.cmdline))
            return True  # Already running, consider success

        # Start the frontend process
        self.logger.info("Starting frontend process: npm run dev")

        # Create command to start the frontend process
        frontend_cmd = AsyncCommand(
            args=['npm', 'run', 'dev'],
            cwd=self.frontend_dir
        )

        result = await frontend_cmd.execute()
        return result.success

    async def uninstall(self) -> bool:
        """
        Uninstall the frontend by stopping the development server process.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Stopping frontend deployment")

        # Find running frontend processes
        from deployment.utils import is_frontend_running
        frontend_status = await is_frontend_running(
            str(self.project_root), str(self.frontend_dir))

        if not frontend_status.found:
            self.logger.info("No frontend processes found to stop")
            return True  # No processes to stop, consider success

        self.logger.info(
            "Found %d frontend process(es) to stop", frontend_status.total_count)

        success_count = 0
        for proc in frontend_status.processes:
            self.logger.info(
                "Terminating frontend process (PID: %d)", proc.pid)
            # Use AsyncCommand to kill the process
            kill_cmd = AsyncCommand.powershell(f"taskkill /PID {proc.pid} /F")
            result = await kill_cmd.execute()
            if result.success:
                success_count += 1
                self.logger.info("Frontend process %d terminated successfully", proc.pid)
            else:
                self.logger.warning("Failed to terminate frontend process %d", proc.pid)

        return success_count == frontend_status.total_count

    async def validate(self) -> bool:
        """
        Validate that the frontend can be deployed.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating frontend deployment environment")

        # Check if npm is available
        npm_version_cmd = AsyncCommand.cmd("npm --version")
        result = await npm_version_cmd.execute()
        if not result.success:
            self.logger.error("NPM is not available. Please ensure Node.js and npm are installed")
            return False
        self.logger.info("NPM is available: %s", result.stdout.strip())

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
                    check=True,
                    shell=True
                )
                npm_version = result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            # Check for log files
            log_dir = self.frontend_dir / 'logs'
            stdout_log = log_dir / 'frontend_stdout.log'
            stderr_log = log_dir / 'frontend_stderr.log'

            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "package_json_exists": package_json_exists,
                "package_json_path": str(package_json) if package_json_exists else None,
                "node_modules_exists": node_modules_exists,
                "node_modules_path": str(node_modules) if node_modules_exists else None,
                "npm_version": npm_version,
                "log_directory": str(log_dir),
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
                "stdout_log_exists": stdout_log.exists(),
                "stderr_log_exists": stderr_log.exists()
            })
        except Exception as e:
            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "error": str(e)
            })
        return metadata

    def is_process_running(self) -> bool:
        """
        Check if the frontend process is currently running.

        Returns:
            bool: True if process is running, False otherwise
        """
        from deployment.utils import is_frontend_running
        frontend_status = is_frontend_running(
            str(self.project_root), str(self.frontend_dir))
        return frontend_status.found

    def get_process_info(self) -> dict:
        """
        Get information about the current frontend process.

        Returns:
            Dict containing process information
        """
        from deployment.utils import is_frontend_running
        frontend_status = is_frontend_running(
            str(self.project_root), str(self.frontend_dir))

        if not frontend_status.found:
            return {"status": "not_running", "process_count": 0}

        processes_info = []
        for proc in frontend_status.processes:
            processes_info.append({
                "pid": proc.pid,
                "name": proc.name,
                "cmdline": proc.cmdline,
                "cwd": proc.cwd,
                "status": proc.status
            })

        return {
            "status": "running",
            "process_count": frontend_status.total_count,
            "processes": processes_info
        }


__all__ = [
    "NativeFrontendDeployStep"
]
