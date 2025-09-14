"""
Docker Compose gateway for project operations.
"""

import json
import logging
import os
from typing import List, Optional
from ....utils.command import AsyncCommand
from ....utils.logger import get_logger
from .models import ComposeProjectInfo, ComposeServiceInfo, DockerCommandResult


class DockerComposeGateway:
    """Gateway for Docker Compose project operations."""
    logger: logging.Logger = get_logger(__name__)

    def __init__(self, compose_file: str, project_dir: Optional[str] = None):
        """
        Initialize Docker Compose gateway for a specific compose file.

        Args:
            compose_file: Path to the docker-compose.yml file
            project_dir: Project directory (defaults to compose file directory)
        """
        self.compose_file = compose_file
        self.project_dir = project_dir or os.path.dirname(compose_file)

    @classmethod
    async def up(cls, compose_file: str, project_dir: Optional[str] = None,
                 detached: bool = True, build: bool = False) -> DockerCommandResult:
        """Start compose services."""
        cls.logger.info("Starting compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("up")
        if detached:
            cmd_parts.append("-d")
        if build:
            cmd_parts.append("--build")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="up",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir,
                "detached": detached,
                "build": build
            }
        )

    @classmethod
    async def down(cls, compose_file: str, project_dir: Optional[str] = None,
                   remove_volumes: bool = False) -> DockerCommandResult:
        """Stop and remove compose services."""
        cls.logger.info("Stopping compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("down")
        if remove_volumes:
            cmd_parts.append("-v")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="down",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir,
                "remove_volumes": remove_volumes
            }
        )

    @classmethod
    async def restart(cls, compose_file: str, project_dir: Optional[str] = None) -> DockerCommandResult:
        """Restart compose services."""
        cls.logger.info("Restarting compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("restart")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="restart",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir
            }
        )

    @classmethod
    async def stop(cls, compose_file: str, project_dir: Optional[str] = None) -> DockerCommandResult:
        """Stop compose services."""
        cls.logger.info("Stopping compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("stop")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="stop",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir
            }
        )

    @classmethod
    async def start(cls, compose_file: str, project_dir: Optional[str] = None) -> DockerCommandResult:
        """Start compose services."""
        cls.logger.info("Starting compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("start")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="start",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir
            }
        )

    @classmethod
    async def pull(cls, compose_file: str, project_dir: Optional[str] = None) -> DockerCommandResult:
        """Pull compose service images."""
        cls.logger.info("Pulling images for compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("pull")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="pull",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir
            }
        )

    @classmethod
    async def build(cls, compose_file: str, project_dir: Optional[str] = None) -> DockerCommandResult:
        """Build compose service images."""
        cls.logger.info("Building images for compose project: %s", compose_file)

        cmd_parts = ["docker", "compose", "-f", compose_file]
        if project_dir:
            cmd_parts.extend(["--project-directory", project_dir])

        cmd_parts.append("build")

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="build",
            parsed_data={
                "compose_file": compose_file,
                "project_dir": project_dir
            }
        )

    @classmethod
    async def list(cls) -> List[ComposeProjectInfo]:
        """List all available compose projects."""
        cls.logger.info("Listing all compose projects")

        # Get all compose projects using docker compose ls
        command = "docker compose ls --format json"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        if not result.success:
            cls.logger.error("Failed to list compose projects: %s", result.stderr)
            return []

        projects = []
        lines = result.stdout.strip().split('\n')

        for line in lines:
            if line.strip():
                try:
                    project_data = json.loads(line)
                    project_info = ComposeProjectInfo(
                        name=project_data.get('Name', ''),
                        status=project_data.get('Status', ''),
                        config_files=project_data.get('ConfigFiles', []),
                        working_dir=project_data.get('WorkingDir', ''),
                        services=project_data.get('Services', []),
                        networks=project_data.get('Networks', []),
                        volumes=project_data.get('Volumes', [])
                    )
                    projects.append(project_info)
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue

        cls.logger.info("Successfully listed %d compose projects", len(projects))
        return projects

    async def exec(self, service: str, command: str) -> DockerCommandResult:
        """Execute a command in a compose service."""
        self.logger.info("Executing command in service %s: %s", service, command)

        cmd_parts = ["docker", "compose", "-f", self.compose_file]
        if self.project_dir:
            cmd_parts.extend(["--project-directory", self.project_dir])

        cmd_parts.extend(["exec", service, command])

        full_command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(full_command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="exec",
            parsed_data={
                "compose_file": self.compose_file,
                "project_dir": self.project_dir,
                "service": service,
                "executed_command": command
            }
        )

    async def logs(self, service: Optional[str] = None, tail_lines: int = 100) -> DockerCommandResult:
        """Get logs from compose services."""
        self.logger.info("Getting logs for compose project: %s", self.compose_file)

        cmd_parts = ["docker", "compose", "-f", self.compose_file]
        if self.project_dir:
            cmd_parts.extend(["--project-directory", self.project_dir])

        cmd_parts.extend(["logs", "--tail", str(tail_lines)])
        if service:
            cmd_parts.append(service)

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            operation="logs",
            parsed_data={
                "compose_file": self.compose_file,
                "project_dir": self.project_dir,
                "service": service,
                "tail_lines": tail_lines
            }
        )

    async def ps(self) -> List[ComposeServiceInfo]:
        """List services in the compose project."""
        self.logger.info("Listing services for compose project: %s", self.compose_file)

        cmd_parts = ["docker", "compose", "-f", self.compose_file]
        if self.project_dir:
            cmd_parts.extend(["--project-directory", self.project_dir])

        cmd_parts.extend(["ps", "--format", "json"])

        command = " ".join(cmd_parts)
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        if not result.success:
            self.logger.error("Failed to list compose services: %s", result.stderr)
            return []

        services = []
        lines = result.stdout.strip().split('\n')

        for line in lines:
            if line.strip():
                try:
                    service_data = json.loads(line)
                    service_info = ComposeServiceInfo(
                        name=service_data.get('Name', ''),
                        project=service_data.get('Project', ''),
                        status=service_data.get('State', ''),
                        image=service_data.get('Image', ''),
                        ports=service_data.get('Ports', []),
                        networks=service_data.get('Networks', []),
                        depends_on=service_data.get('DependsOn', [])
                    )
                    services.append(service_info)
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue

        self.logger.info("Successfully listed %d compose services", len(services))
        return services


__all__ = [
    "DockerComposeGateway"
]
