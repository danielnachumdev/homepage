"""
Data models for Docker gateway operations.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from ....utils.command import CommandExecutionResult


@dataclass
class ContainerInfo:
    """Normalized container information from docker ps --format json."""
    id: str
    image: str
    command: str
    created_at: str
    state: str
    status: str
    ports: str
    names: str
    running_for: str
    size: str
    labels: str
    local_volumes: str
    platform: Dict[str, str]


@dataclass
class ComposeProjectInfo:
    """Normalized compose project information."""
    name: str
    status: str
    config_files: List[str]
    working_dir: str
    services: List[str]
    networks: List[str]
    volumes: List[str]


@dataclass
class ComposeServiceInfo:
    """Normalized compose service information."""
    name: str
    project: str
    status: str
    image: str
    ports: List[str]
    networks: List[str]
    depends_on: List[str]


@dataclass
class DockerCommandResult:
    """Enriched result of a Docker command execution."""
    raw: CommandExecutionResult
    container_name: Optional[str] = None
    operation: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None

    @property
    def success(self) -> bool:
        """Convenience property to access raw success."""
        return self.raw.success

    @property
    def stdout(self) -> str:
        """Convenience property to access raw stdout."""
        return self.raw.stdout

    @property
    def stderr(self) -> str:
        """Convenience property to access raw stderr."""
        return self.raw.stderr

    @property
    def return_code(self) -> int:
        """Convenience property to access raw return code."""
        return self.raw.return_code

    @property
    def execution_time(self) -> float:
        """Convenience property to access raw execution time."""
        return self.raw.execution_time


@dataclass
class ContainerInspectInfo:
    """Detailed container information from docker inspect."""
    id: str
    name: str
    image: str
    image_id: str
    created: str
    state: str
    status: str
    health_status: Optional[str]
    ports: List[Dict[str, str]]
    mounts: List[Dict[str, Any]]
    networks: List[str]
    environment_vars: Dict[str, str]
    command: List[str]
    entrypoint: List[str]
    working_dir: str
    user: str
    restart_policy: Optional[str]
    labels: Dict[str, str]


__all__ = [
    "ContainerInfo",
    "ComposeProjectInfo",
    "ComposeServiceInfo",
    "DockerCommandResult",
    "ContainerInspectInfo"
]
