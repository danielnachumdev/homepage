"""
Docker deployment step for the homepage project.

This step handles deploying the application using Docker Compose.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List
from deployment.steps.base_step import Step
from backend.src.utils.command import AsyncCommand
from backend.src.gateways.v1.docker_gateway.compose import DockerComposeGateway


class DockerDeployStep(Step):
    """
    Step that deploys the homepage application using Docker Compose.

    This step will:
    - Install: Run 'docker compose up -d --build' to start the services
    - Uninstall: Run 'docker compose down' to stop and remove the services
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 compose_file: Optional[str] = None,
                 name: str = "docker-deploy",
                 description: str = "Deploy homepage using Docker Compose"):
        """
        Initialize the Docker deployment step.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            compose_file: Path to docker-compose.yml file (defaults to 'docker-compose.yml' in project root)
            name: Name for this step
            description: Description of what this step does
        """
        super().__init__(name, description)

        # Set project root - default to current working directory
        if project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)

        # Set compose file path
        if compose_file is None:
            self.compose_file = self.project_root / "docker-compose.yml"
        else:
            self.compose_file = Path(compose_file)

    async def install(self) -> bool:
        """
        Install the application using Docker Compose.

        Returns:
            bool: True if installation was successful, False otherwise
        """
        # Display warnings about Docker deployment limitations
        self.logger.warning("=" * 60)
        self.logger.warning("DOCKER DEPLOYMENT WARNING")
        self.logger.warning("=" * 60)
        self.logger.warning("You are deploying using Docker containers.")
        self.logger.warning(
            "This deployment method may limit some functionalities:")
        self.logger.warning("- Limited access to host system resources")
        self.logger.warning("- Potential networking restrictions")
        self.logger.warning(
            "- Reduced performance compared to native deployment")
        self.logger.warning("- May not support all system integrations")
        self.logger.warning("")
        self.logger.warning(
            "For full functionality, consider using native deployment instead.")
        self.logger.warning("=" * 60)

        self.logger.info(
            "Starting Docker deployment for project at %s", self.project_root)

        # Check if docker-compose.yml exists
        if not self.compose_file.exists():
            self.logger.error(
                "Docker compose file not found: %s", self.compose_file)
            return False

        # Use DockerComposeGateway for the actual deployment
        try:
            result = await DockerComposeGateway.up(
                compose_file=str(self.compose_file),
                project_dir=str(self.project_root),
                detached=True,
                build=True
            )

            if result.raw.success:
                self.logger.info("Docker compose up completed successfully")
                self.logger.debug("Docker compose output: %s", result.raw.stdout)
                if result.raw.stderr:
                    self.logger.warning("Docker compose warnings: %s", result.raw.stderr)
                return True
            else:
                self.logger.error("Failed to start Docker services: %s", result.raw.stderr)
                return False

        except Exception as e:
            self.logger.error("Unexpected error during Docker deployment: %s", e)
            return False

    async def uninstall(self) -> bool:
        """
        Uninstall the application by stopping Docker Compose services.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info(
            "Stopping Docker deployment for project at %s", self.project_root)

        # Check if docker-compose.yml exists
        if not self.compose_file.exists():
            self.logger.warning(
                "Docker compose file not found: %s", self.compose_file)
            # Consider this a success since there's nothing to uninstall
            return True

        # Use DockerComposeGateway for the actual uninstallation
        try:
            result = await DockerComposeGateway.down(
                compose_file=str(self.compose_file),
                project_dir=str(self.project_root),
                remove_volumes=False
            )

            if result.raw.success:
                self.logger.info("Docker compose down completed successfully")
                self.logger.debug("Docker compose output: %s", result.raw.stdout)
                if result.raw.stderr:
                    self.logger.warning("Docker compose warnings: %s", result.raw.stderr)
                return True
            else:
                self.logger.error("Failed to stop Docker services: %s", result.raw.stderr)
                return False

        except Exception as e:
            self.logger.error("Unexpected error during Docker uninstallation: %s", e)
            return False

    async def validate(self) -> bool:
        """
        Validate that Docker and docker-compose.yml are available.

        Returns:
            bool: True if validation passes, False otherwise
        """
        # Display warnings about Docker deployment limitations
        self.logger.warning(
            "Docker deployment validation - functionality limitations may apply")

        self.logger.info("Validating Docker deployment environment")

        # Check if Docker is available
        docker_version_cmd = AsyncCommand.cmd("docker --version")
        result = await docker_version_cmd.execute()
        if not result.success:
            self.logger.error("Docker is not available or not working properly")
            return False
        self.logger.info("Docker found: %s", result.stdout.strip())

        # Check if docker-compose.yml exists
        if not self.compose_file.exists():
            self.logger.error(
                "Docker compose file not found: %s", self.compose_file)
            return False

        self.logger.info("Docker compose file found: %s", self.compose_file)

        # Check if project root is accessible
        if not self.project_root.exists() or not self.project_root.is_dir():
            self.logger.error(
                "Project root directory not accessible: %s", self.project_root)
            return False

        self.logger.info(
            "Project root directory accessible: %s", self.project_root)

        # Try to validate the docker-compose.yml file
        config_cmd = AsyncCommand.cmd(
            f"docker compose -f {self.compose_file} config",
            cwd=self.project_root
        )
        result = await config_cmd.execute()
        if not result.success:
            self.logger.error("Docker compose configuration is invalid")
            self.logger.error("Error output: %s", result.stderr)
            return False

        self.logger.info("Docker compose configuration is valid")
        self.logger.info("Docker deployment validation passed")
        return True

    async def get_metadata(self) -> dict:
        """
        Get metadata about this step including Docker-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = await super().get_metadata()
        metadata.update({
            "project_root": str(self.project_root),
            "compose_file": str(self.compose_file),
            "compose_file_exists": self.compose_file.exists(),
            "project_root_exists": self.project_root.exists()
        })
        return metadata


__all__ = [
    "DockerDeployStep"
]
