"""
Windows start on login step for the homepage project.

This step handles creating Windows startup shortcuts that will automatically
launch the frontend and backend services when the user logs in.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from deployment.steps.base_step import Step


class WindowsStartOnLoginStep(Step):
    """
    Step that creates Windows startup shortcuts to automatically launch
    frontend and backend services on user login.

    This step will:
    - Install: Create shortcuts in Windows startup folder pointing to the startup script
    - Uninstall: Remove shortcuts from Windows startup folder
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 frontend_dir: Optional[str] = None,
                 backend_dir: Optional[str] = None,
                 name: str = "windows-start-on-login",
                 description: str = "Create Windows startup shortcuts to auto-launch services"):
        """
        Initialize the Windows start on login step.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            frontend_dir: Path to the frontend directory (defaults to 'frontend' in project root)
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

        # Set directories
        if frontend_dir is None:
            self.frontend_dir = self.project_root / "frontend"
        else:
            self.frontend_dir = Path(frontend_dir)

        if backend_dir is None:
            self.backend_dir = self.project_root / "backend"
        else:
            self.backend_dir = Path(backend_dir)

        # Path to the startup script
        self.startup_script = self.project_root / \
            "deployment" / "scripts" / "startup_launcher.ps1"

        # Windows startup folder path
        self.startup_folder = self._get_startup_folder()

        # Shortcut name
        self.shortcut_name = "Homepage Startup.lnk"

        self.logger.info("WindowsStartOnLoginStep initialized with project_root=%s, startup_folder=%s",
                         self.project_root, self.startup_folder)

    def _get_startup_folder(self) -> Path:
        """
        Get the Windows startup folder path.

        Returns:
            Path to the Windows startup folder
        """
        try:
            # Get the user's startup folder
            startup_path = os.path.expanduser(
                "~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            return Path(startup_path)
        except Exception as e:
            self.logger.error("Failed to get startup folder path: %s", e)
            # Fallback to a relative path
            return Path("startup")

    def _create_shortcut(self, target_path: str, shortcut_path: str, arguments: str = "",
                         working_directory: str = "", description: str = "") -> bool:
        """
        Create a Windows shortcut using PowerShell.

        Args:
            target_path: Path to the target executable/script
            shortcut_path: Path where the shortcut should be created
            arguments: Command line arguments for the target
            working_directory: Working directory for the target
            description: Description for the shortcut

        Returns:
            True if shortcut was created successfully, False otherwise
        """
        try:
            # PowerShell script to create shortcut
            ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.Arguments = "{arguments}"
$Shortcut.WorkingDirectory = "{working_directory}"
$Shortcut.Description = "{description}"
$Shortcut.Save()
"""

            # Execute PowerShell script
            subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                check=True
            )
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error("Failed to create shortcut: %s", e.stderr)
            return False
        except Exception as e:
            self.logger.error("Unexpected error creating shortcut: %s", e)
            return False

    def _remove_shortcut(self, shortcut_path: str) -> bool:
        """
        Remove a Windows shortcut.

        Args:
            shortcut_path: Path to the shortcut to remove

        Returns:
            True if shortcut was removed successfully, False otherwise
        """
        try:
            shortcut_file = Path(shortcut_path)
            if shortcut_file.exists():
                shortcut_file.unlink()
                self.logger.info("Removed shortcut: %s", shortcut_path)
                return True
            else:
                self.logger.warning("Shortcut not found: %s", shortcut_path)
                return True  # Consider it successful if it doesn't exist
        except Exception as e:
            self.logger.error("Failed to remove shortcut: %s", e)
            return False

    def install(self) -> bool:
        """
        Install the startup shortcuts.

        Creates shortcuts in the Windows startup folder that will launch
        the frontend and backend services on user login.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        self.logger.info("Creating Windows startup shortcuts")

        try:
            # Check if we're on Windows
            if os.name != 'nt':
                self.logger.error("This step is only supported on Windows")
                return False

            # Check if startup script exists
            if not self.startup_script.exists():
                self.logger.error(
                    "Startup script not found: %s", self.startup_script)
                return False

            # Ensure startup folder exists
            if not self.startup_folder.exists():
                self.logger.info("Creating startup folder: %s",
                                 self.startup_folder)
                self.startup_folder.mkdir(parents=True, exist_ok=True)

            # Check if startup folder is writable
            if not os.access(self.startup_folder, os.W_OK):
                self.logger.error(
                    "Startup folder is not writable: %s", self.startup_folder)
                return False

            # Create the shortcut
            shortcut_path = self.startup_folder / self.shortcut_name

            # Prepare arguments for the PowerShell script
            arguments = f'-ProjectRoot "{self.project_root}" -FrontendDir "{self.frontend_dir}" -BackendDir "{self.backend_dir}"'

            success = self._create_shortcut(
                target_path="powershell.exe",
                shortcut_path=str(shortcut_path),
                arguments=f'-ExecutionPolicy Bypass -File "{self.startup_script}" {arguments}',
                working_directory=str(self.project_root),
                description="Auto-start Homepage Frontend and Backend Services"
            )

            if success:
                self.logger.info(
                    "Startup shortcut created successfully: %s", shortcut_path)
                self._mark_installed()
                return True
            else:
                self.logger.error("Failed to create startup shortcut")
                return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during startup shortcut installation: %s", e)
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the startup shortcuts.

        Removes shortcuts from the Windows startup folder.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info("Removing Windows startup shortcuts")

        try:
            # Check if we're on Windows
            if os.name != 'nt':
                self.logger.error("This step is only supported on Windows")
                return False

            # Remove the shortcut
            shortcut_path = self.startup_folder / self.shortcut_name
            success = self._remove_shortcut(str(shortcut_path))

            if success:
                self.logger.info("Startup shortcut removed successfully")
                self._mark_uninstalled()
                return True
            else:
                self.logger.error("Failed to remove startup shortcut")
                return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during startup shortcut uninstallation: %s", e)
            return False

    def validate(self) -> bool:
        """
        Validate that startup shortcuts can be created.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.logger.info("Validating Windows startup environment")

        try:
            # Check if we're on Windows
            if os.name != 'nt':
                self.logger.error("This step is only supported on Windows")
                return False

            # Check if startup script exists
            if not self.startup_script.exists():
                self.logger.error(
                    "Startup script not found: %s", self.startup_script)
                return False

            self.logger.info("Startup script found: %s", self.startup_script)

            # Check if startup folder exists or can be created
            if not self.startup_folder.exists():
                self.logger.info(
                    "Startup folder does not exist, will be created: %s", self.startup_folder)
            else:
                self.logger.info("Startup folder found: %s",
                                 self.startup_folder)

            # Check if startup folder is writable
            if not os.access(self.startup_folder, os.W_OK):
                self.logger.error(
                    "Startup folder is not writable: %s", self.startup_folder)
                return False

            # Check if PowerShell is available
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 'Get-Host'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.logger.info("PowerShell is available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error("PowerShell is not available")
                return False

            # Check if directories exist
            if not self.frontend_dir.exists():
                self.logger.error(
                    "Frontend directory not found: %s", self.frontend_dir)
                return False

            if not self.backend_dir.exists():
                self.logger.error(
                    "Backend directory not found: %s", self.backend_dir)
                return False

            self.logger.info("Windows startup validation passed")
            return True

        except Exception as e:
            self.logger.error("Windows startup validation failed: %s", e)
            return False

    def get_metadata(self) -> dict:
        """
        Get metadata about this step including Windows-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = super().get_metadata()

        try:
            # Check if startup script exists
            startup_script_exists = self.startup_script.exists()

            # Check if startup folder exists
            startup_folder_exists = self.startup_folder.exists()

            # Check if startup folder is writable
            startup_folder_writable = os.access(
                self.startup_folder, os.W_OK) if startup_folder_exists else False

            # Check if shortcut already exists
            shortcut_path = self.startup_folder / self.shortcut_name
            shortcut_exists = shortcut_path.exists()

            # Check PowerShell availability
            powershell_available = False
            try:
                subprocess.run(['powershell', '-Command', 'Get-Host'],
                               capture_output=True, check=True)
                powershell_available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "backend_dir": str(self.backend_dir),
                "startup_script": str(self.startup_script),
                "startup_script_exists": startup_script_exists,
                "startup_folder": str(self.startup_folder),
                "startup_folder_exists": startup_folder_exists,
                "startup_folder_writable": startup_folder_writable,
                "shortcut_name": self.shortcut_name,
                "shortcut_path": str(shortcut_path),
                "shortcut_exists": shortcut_exists,
                "powershell_available": powershell_available,
                "platform": os.name
            })
        except Exception as e:
            metadata.update({
                "project_root": str(self.project_root),
                "frontend_dir": str(self.frontend_dir),
                "backend_dir": str(self.backend_dir),
                "error": str(e)
            })

        return metadata

    def is_shortcut_installed(self) -> bool:
        """
        Check if the startup shortcut is currently installed.

        Returns:
            bool: True if shortcut exists, False otherwise
        """
        shortcut_path = self.startup_folder / self.shortcut_name
        return shortcut_path.exists()

    def get_shortcut_info(self) -> dict:
        """
        Get information about the current startup shortcut.

        Returns:
            Dict containing shortcut information
        """
        shortcut_path = self.startup_folder / self.shortcut_name

        if not shortcut_path.exists():
            return {"status": "not_installed"}

        try:
            stat = shortcut_path.stat()
            return {
                "status": "installed",
                "path": str(shortcut_path),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime
            }
        except Exception as e:
            return {
                "status": "error",
                "path": str(shortcut_path),
                "error": str(e)
            }


__all__ = [
    "WindowsStartOnLoginStep"
]
