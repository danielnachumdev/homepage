"""
Docker deployment strategy for the homepage project.

This strategy deploys the entire homepage application using Docker Compose.
"""

from typing import List, Optional
from deployment.strategies.base_strategy import Strategy
from deployment.steps.docker_deploy_step import DockerDeployStep


class DockerDeployStrategy(Strategy):
    """
    Strategy that deploys the homepage application using Docker Compose.

    This strategy contains a single DockerDeployStep that handles the complete
    deployment process using docker-compose.
    """

    def __init__(self,
                 project_root: Optional[str] = None,
                 compose_file: Optional[str] = None,
                 name: str = "docker-deploy",
                 description: str = "Deploy homepage using Docker Compose"):
        """
        Initialize the Docker deployment strategy.

        Args:
            project_root: Path to the project root directory (defaults to current working directory)
            compose_file: Path to docker-compose.yml file (defaults to 'docker-compose.yml' in project root)
            name: Name for this strategy
            description: Description of what this strategy does
        """
        super().__init__(name, description)

        self.project_root = project_root
        self.compose_file = compose_file

        self.logger.info("DockerDeployStrategy initialized with project_root=%s, compose_file=%s",
                         self.project_root, self.compose_file)

    def get_steps(self) -> List[DockerDeployStep]:
        """
        Get the ordered list of steps for this strategy.

        This strategy contains a single DockerDeployStep that handles the complete
        deployment process.

        Returns:
            List containing a single DockerDeployStep instance
        """
        # Create the Docker deployment step
        docker_step = DockerDeployStep(
            project_root=self.project_root,
            compose_file=self.compose_file,
            name="docker-deploy-step",
            description="Deploy homepage application using Docker Compose"
        )

        return [docker_step]

    def get_metadata(self) -> dict:
        """
        Get metadata about this strategy including Docker-specific information.

        Returns:
            Dict containing strategy metadata
        """
        metadata = super().get_metadata()
        metadata.update({
            "project_root": self.project_root,
            "compose_file": self.compose_file,
            "deployment_type": "docker-compose"
        })
        return metadata


__all__ = [
    "DockerDeployStrategy"
]
