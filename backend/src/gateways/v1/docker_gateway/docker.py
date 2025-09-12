"""
Docker gateway for container operations.
"""

import json
import logging
from typing import List, Optional
from ....utils.command import AsyncCommand
from ....utils.logger import get_logger
from .models import ContainerInfo, DockerCommandResult, ContainerInspectInfo


class DockerGateway:
    """Gateway for Docker container operations."""
    logger: logging.Logger = get_logger(__name__)

    def __init__(self, container_name: str):
        """
        Initialize Docker gateway for a specific container.

        Args:
            container_name: Name of the container to operate on
        """
        self.container_name = container_name

    @classmethod
    async def start(cls, container_name: str) -> DockerCommandResult:
        """Start a Docker container."""

        cls.logger.info("Starting container: %s", container_name)

        command = f"docker start {container_name}"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            container_name=container_name,
            operation="start"
        )

    @classmethod
    async def stop(cls, container_name: str) -> DockerCommandResult:
        """Stop a Docker container."""
        cls.logger.info("Stopping container: %s", container_name)

        command = f"docker stop {container_name}"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            container_name=container_name,
            operation="stop"
        )

    @classmethod
    async def restart(cls, container_name: str) -> DockerCommandResult:
        """Restart a Docker container."""

        cls.logger.info("Restarting container: %s", container_name)

        command = f"docker restart {container_name}"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            container_name=container_name,
            operation="restart"
        )

    @classmethod
    async def delete(cls, container_name: str, force: bool = False) -> DockerCommandResult:
        """Delete a Docker container."""

        cls.logger.info("Deleting container: %s (force=%s)", container_name, force)

        flag = "-f" if force else ""
        command = f"docker rm {flag} {container_name}".strip()
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            container_name=container_name,
            operation="delete",
            parsed_data={"force": force}
        )

    @classmethod
    async def list(cls, all_containers: bool = False) -> List[ContainerInfo]:
        """List all Docker containers."""

        cls.logger.info("Listing containers (all_containers=%s)", all_containers)

        flag = "-a" if all_containers else ""
        command = f"docker ps {flag} --format json"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        if not result.success:
            cls.logger.error("Failed to list containers: %s", result.stderr)
            return []

        containers = []
        lines = result.stdout.strip().split('\n')

        for line in lines:
            if line.strip():
                try:
                    container_data = json.loads(line)
                    # Filter out invalid entries
                    if all(key in container_data for key in ['ID', 'Image', 'Command', 'CreatedAt', 'Status']):
                        container_info = ContainerInfo(
                            id=container_data.get('ID', ''),
                            image=container_data.get('Image', ''),
                            command=container_data.get('Command', ''),
                            created_at=container_data.get('CreatedAt', ''),
                            state=container_data.get('State', ''),
                            status=container_data.get('Status', ''),
                            ports=container_data.get('Ports', ''),
                            names=container_data.get('Names', ''),
                            running_for=container_data.get('RunningFor', ''),
                            size=container_data.get('Size', ''),
                            labels=container_data.get('Labels', ''),
                            local_volumes=container_data.get('LocalVolumes', ''),
                            platform={
                                'architecture': container_data.get('Platform', {}).get('architecture', ''),
                                'os': container_data.get('Platform', {}).get('os', '')
                            }
                        )
                        containers.append(container_info)
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue

        cls.logger.info("Successfully listed %d containers", len(containers))
        return containers

    async def inspect(self) -> Optional[ContainerInspectInfo]:
        """Get detailed information about the container."""
        self.logger.info("Inspecting container: %s", self.container_name)

        command = f"docker inspect {self.container_name} --format json"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        if not result.success:
            self.logger.error("Failed to inspect container %s: %s", self.container_name, result.stderr)
            return None

        try:
            container_data = json.loads(result.stdout)

            # Extract ports
            ports = []
            network_settings = container_data.get("NetworkSettings", {})
            if "Ports" in network_settings:
                for port_binding, host_bindings in network_settings["Ports"].items():
                    if host_bindings:
                        for host_binding in host_bindings:
                            ports.append({
                                "container_port": port_binding,
                                "host_ip": host_binding.get("HostIp", ""),
                                "host_port": host_binding.get("HostPort", "")
                            })

            # Extract mounts
            mounts = []
            for mount in container_data.get("Mounts", []):
                mounts.append({
                    "source": mount.get("Source", ""),
                    "destination": mount.get("Destination", ""),
                    "type": mount.get("Type", ""),
                    "read_only": not mount.get("RW", True)
                })

            # Extract networks
            networks = []
            if "Networks" in network_settings:
                networks = list(network_settings["Networks"].keys())

            # Extract environment variables
            env_vars = {}
            for env in container_data.get("Config", {}).get("Env", []):
                if '=' in env:
                    key, value = env.split('=', 1)
                    env_vars[key] = value

            # Extract labels
            labels = container_data.get("Config", {}).get("Labels", {})

            return ContainerInspectInfo(
                id=container_data.get("Id", ""),
                name=container_data.get("Name", "").lstrip('/'),
                image=container_data.get("Config", {}).get("Image", ""),
                image_id=container_data.get("Image", ""),
                created=container_data.get("Created", ""),
                state=container_data.get("State", {}).get("Status", ""),
                status=container_data.get("State", {}).get("Status", ""),
                health_status=container_data.get("State", {}).get("Health", {}).get("Status") if container_data.get(
                    "State", {}).get("Health") else None,
                ports=ports,
                mounts=mounts,
                networks=networks,
                environment_vars=env_vars,
                command=container_data.get("Config", {}).get("Cmd", []),
                entrypoint=container_data.get("Config", {}).get("Entrypoint", []),
                working_dir=container_data.get("Config", {}).get("WorkingDir", ""),
                user=container_data.get("Config", {}).get("User", ""),
                restart_policy=container_data.get("HostConfig", {}).get("RestartPolicy", {}).get("Name"),
                labels=labels
            )

        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse container JSON for %s: %s", self.container_name, str(e))
            return None

    async def logs(self, tail_lines: int = 100) -> DockerCommandResult:
        """Get logs from the container."""
        self.logger.info("Getting logs for container: %s (tail=%d)", self.container_name, tail_lines)

        command = f"docker logs --tail {tail_lines} {self.container_name}"
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            container_name=self.container_name,
            operation="logs",
            parsed_data={"tail_lines": tail_lines}
        )

    async def exec(self, command: str) -> DockerCommandResult:
        """Execute a command in the container."""
        self.logger.info("Running command in container %s: %s", self.container_name, command)

        full_command = f"docker exec {self.container_name} {command}"
        async_cmd = AsyncCommand.cmd(full_command)
        result = await async_cmd.execute()

        return DockerCommandResult(
            raw=result,
            container_name=self.container_name,
            operation="run",
            parsed_data={"executed_command": command}
        )


__all__ = [
    "DockerGateway"
]
