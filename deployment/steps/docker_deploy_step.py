"""
Docker deployment step for the homepage project.

This step handles deploying the application using Docker Compose.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from deployment.steps.base_step import Step
from deployment.utils.process_manager import ProcessManager


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

    def install(self) -> bool:
        """
        Install the application using Docker Compose.

        Runs 'docker compose up -d --build' to start the services.

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

        try:
            # Check if docker-compose.yml exists
            if not self.compose_file.exists():
                self.logger.error(
                    "Docker compose file not found: %s", self.compose_file)
                return False

            # Run docker compose up -d --build using ProcessManager
            self.logger.info(
                "Running: docker compose -f %s up -d --build", self.compose_file)

            result = ProcessManager.spawn(
                command=['docker', 'compose', '-f',
                         str(self.compose_file), 'up', '-d', '--build'],
                detached=False,
                cwd=self.project_root,
                log_dir=self.project_root / 'logs',
                log_prefix='docker_compose_up'
            )

            if not result.success:
                self.logger.error(
                    "Failed to start Docker services: %s", result.error_message)
                return False

            # Wait for the process to complete
            if result.process:
                stdout, stderr = result.process.communicate()

                self.logger.info("Docker compose up completed successfully")
                self.logger.debug("Docker compose output: %s", stdout)

                if stderr:
                    self.logger.warning("Docker compose warnings: %s", stderr)

            self._mark_installed()
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Docker compose up failed with return code %d", e.returncode)
            self.logger.error("Error output: %s", e.stderr)
            if e.stdout:
                self.logger.error("Standard output: %s", e.stdout)
            return False

        except FileNotFoundError:
            self.logger.error(
                "Docker command not found. Please ensure Docker is installed and in PATH")
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during Docker deployment: %s", e)
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the application by stopping Docker Compose services.

        Runs 'docker compose down' to stop and remove the services.

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        self.logger.info(
            "Stopping Docker deployment for project at %s", self.project_root)

        try:
            # Check if docker-compose.yml exists
            if not self.compose_file.exists():
                self.logger.warning(
                    "Docker compose file not found: %s", self.compose_file)
                # Consider this a success since there's nothing to uninstall
                self._mark_uninstalled()
                return True

            # Run docker compose down using ProcessManager
            self.logger.info(
                "Running: docker compose -f %s down", self.compose_file)

            result = ProcessManager.spawn(
                command=['docker', 'compose', '-f',
                         str(self.compose_file), 'down'],
                detached=False,
                cwd=self.project_root,
                log_dir=self.project_root / 'logs',
                log_prefix='docker_compose_down'
            )

            if not result.success:
                self.logger.error(
                    "Failed to stop Docker services: %s", result.error_message)
                return False

            # Wait for the process to complete
            if result.process:
                stdout, stderr = result.process.communicate()

                self.logger.info("Docker compose down completed successfully")
                self.logger.debug("Docker compose output: %s", stdout)

                if stderr:
                    self.logger.warning("Docker compose warnings: %s", stderr)

            self._mark_uninstalled()
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Docker compose down failed with return code %d", e.returncode)
            self.logger.error("Error output: %s", e.stderr)
            if e.stdout:
                self.logger.error("Standard output: %s", e.stdout)
            return False

        except FileNotFoundError:
            self.logger.error(
                "Docker command not found. Please ensure Docker is installed and in PATH")
            return False

        except Exception as e:
            self.logger.error(
                "Unexpected error during Docker uninstallation: %s", e)
            return False

    def validate(self) -> bool:
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
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("Docker found: %s", result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error(
                "Docker is not available or not working properly")
            return False

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
        try:
            result = subprocess.run(
                ['docker', 'compose', '-f', str(self.compose_file), 'config'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("Docker compose configuration is valid")
        except subprocess.CalledProcessError as e:
            self.logger.error("Docker compose configuration is invalid")
            self.logger.error("Error output: %s", e.stderr)
            return False

        self.logger.info("Docker deployment validation passed")
        return True

    def get_metadata(self) -> dict:
        """
        Get metadata about this step including Docker-specific information.

        Returns:
            Dict containing step metadata
        """
        metadata = super().get_metadata()
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
