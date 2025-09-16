"""
Windows native deployment strategy for the homepage project.

This strategy deploys the entire homepage application using native Windows processes
and creates startup shortcuts for automatic launch on login.
"""

from typing import List, Optional
from deployment.strategies.base_strategy import Strategy
from deployment.steps import NativeBackendDependencyInstallStep, NativeBackendDeployStep, \
    NativeFrontendDependencyInstallStep, NativeFrontendDeployStep, WindowsStartOnLoginStep, Step


class WindowsNativeDeployStrategy(Strategy):
    """
    Strategy that deploys the homepage application using native Windows processes.
    
    This strategy:
    1. Installs backend Python dependencies
    2. Installs frontend Node.js dependencies  
    3. Starts the backend server process
    4. Starts the frontend development server
    5. Creates Windows startup shortcuts for automatic launch
    
    The strategy ensures proper port synchronization and careful process management.
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 backend_dir: Optional[str] = None,
                 frontend_dir: Optional[str] = None,
                 backend_port: int = 8000,
                 frontend_port: int = 5173,
                 name: str = "windows-native-deploy",
                 description: str = "Deploy homepage using native Windows processes with startup shortcuts"):
        """
        Initialize the Windows native deployment strategy.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            backend_dir: Path to the backend directory (defaults to 'backend' in project root)
            frontend_dir: Path to the frontend directory (defaults to 'frontend' in project root)
            backend_port: Port for the backend server (default: 8000)
            frontend_port: Port for the frontend development server (default: 5173)
            name: Name for this strategy
            description: Description of what this strategy does
        """
        super().__init__(name, description)

        self.project_root = project_root
        self.backend_dir = backend_dir
        self.frontend_dir = frontend_dir
        self.backend_port = backend_port
        self.frontend_port = frontend_port

    def get_steps(self) -> List[Step]:
        """
        Get the ordered list of steps for this strategy.

        Returns:
            List of Step instances in installation order
        """
        steps: List[Step] = []

        # Step 1: Install backend dependencies
        backend_deps_step = NativeBackendDependencyInstallStep(
            project_root=self.project_root,
            backend_dir=self.backend_dir,
            name="windows-backend-deps",
            description="Install Python dependencies for backend"
        )
        steps.append(backend_deps_step)

        # Step 2: Install frontend dependencies
        frontend_deps_step = NativeFrontendDependencyInstallStep(
            project_root=self.project_root,
            frontend_dir=self.frontend_dir,
            name="windows-frontend-deps",
            description="Install Node.js dependencies for frontend"
        )
        steps.append(frontend_deps_step)

        # Step 3: Deploy backend server
        backend_deploy_step = NativeBackendDeployStep(
            project_root=self.project_root,
            backend_dir=self.backend_dir,
            name="windows-backend-deploy",
            description="Start backend server process"
        )
        steps.append(backend_deploy_step)

        # Step 4: Deploy frontend development server
        frontend_deploy_step = NativeFrontendDeployStep(
            project_root=self.project_root,
            frontend_dir=self.frontend_dir,
            name="windows-frontend-deploy",
            description="Start frontend development server"
        )
        steps.append(frontend_deploy_step)

        # Step 5: Create Windows startup shortcuts
        startup_step = WindowsStartOnLoginStep(
            project_root=self.project_root,
            frontend_dir=self.frontend_dir,
            backend_dir=self.backend_dir,
            name="windows-startup-shortcuts",
            description="Create Windows startup shortcuts for auto-launch"
        )
        steps.append(startup_step)

        return steps

    async def install(self) -> bool:
        """
        Install all steps in this strategy with port synchronization.

        Returns:
            bool: True if all steps were installed successfully, False otherwise
        """
        self.logger.info(f"Starting Windows native deployment of strategy '{self.name}'")
        self.logger.info(f"Backend port: {self.backend_port}, Frontend port: {self.frontend_port}")

        # Set environment variables for port synchronization
        import os
        os.environ['BACKEND_PORT'] = str(self.backend_port)
        os.environ['FRONTEND_PORT'] = str(self.frontend_port)

        # Call parent install method
        return await super().install()

    async def uninstall(self) -> bool:
        """
        Uninstall all steps in this strategy with careful process management.

        Returns:
            bool: True if all steps were uninstalled successfully, False otherwise
        """
        self.logger.info(f"Starting Windows native uninstallation of strategy '{self.name}'")
        self.logger.info("This will carefully stop all running processes and remove startup shortcuts")

        # Call parent uninstall method
        return await super().uninstall()

    async def get_metadata(self) -> dict:
        """
        Get metadata about this strategy including port information.

        Returns:
            Dict containing strategy metadata
        """
        metadata = await super().get_metadata()
        metadata.update({
            "backend_port": self.backend_port,
            "frontend_port": self.frontend_port,
            "strategy_type": "windows_native",
            "platform": "windows"
        })
        return metadata

    def get_port_info(self) -> dict:
        """
        Get information about the configured ports.

        Returns:
            Dict containing port information
        """
        return {
            "backend_port": self.backend_port,
            "frontend_port": self.frontend_port,
            "backend_url": f"http://localhost:{self.backend_port}",
            "frontend_url": f"http://localhost:{self.frontend_port}"
        }


__all__ = [
    "WindowsNativeDeployStrategy"
]
