from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ContainerStatus(str, Enum):
    """Container status enumeration."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    CREATED = "created"
    EXITED = "exited"
    DEAD = "dead"


class HealthStatus(str, Enum):
    """Container health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    NONE = "none"


class PlatformInfo(BaseModel):
    """Platform information for a container."""
    architecture: str
    os: str


class DockerPsEntry(BaseModel):
    """Represents a single container entry from docker ps --format json."""
    ID: str = Field(..., description="Container ID")
    Image: str = Field(..., description="Container image")
    Command: str = Field(..., description="Container command")
    CreatedAt: str = Field(..., description="Container creation time")
    State: str = Field(...,
                       description="Container state (running, exited, etc.)")
    Status: str = Field(..., description="Container status description")
    Ports: str = Field(..., description="Port mappings")
    Names: str = Field(..., description="Container names")
    Labels: str = Field(..., description="Container labels")
    LocalVolumes: str = Field(..., description="Number of local volumes")
    Mounts: str = Field(..., description="Volume mounts")
    Networks: str = Field(..., description="Network connections")
    Platform: PlatformInfo = Field(..., description="Platform information")
    RunningFor: str = Field(...,
                            description="How long container has been running")
    Size: str = Field(..., description="Container size")


# Legacy schemas for backward compatibility
class DockerRequest(BaseModel):
    """Legacy Docker request schema."""
    container_name: str


class DockerResponse(BaseModel):
    """Legacy Docker response schema."""
    success: bool
    message: str
    error: Optional[str] = None


# Request schemas
class ContainerNameRequest(BaseModel):
    """Request schema for container operations by name."""
    container_name: str


class LogsRequest(BaseModel):
    """Request schema for getting container logs."""
    container_name: str
    tail_lines: int = 100


class RemoveContainerRequest(BaseModel):
    """Request schema for removing a container."""
    container_name: str
    force: bool = False


class RedeployRequest(BaseModel):
    """Request schema for redeploying a container."""
    container_name: str
    image: Optional[str] = None
    environment_vars: Optional[Dict[str, str]] = None
    ports: Optional[Dict[str, str]] = None
    volumes: Optional[List[str]] = None


# Response schemas
class ContainerInfoResponse(BaseModel):
    """Response schema for container information."""
    success: bool
    container_name: str
    container_id: Optional[str] = None
    status: Optional[ContainerStatus] = None
    image: Optional[str] = None
    image_id: Optional[str] = None
    created: Optional[str] = None
    ports: Optional[List[Dict[str, Any]]] = None
    mounts: Optional[List[Dict[str, Any]]] = None
    networks: Optional[List[str]] = None
    health_status: Optional[HealthStatus] = None
    environment_vars: Optional[Dict[str, str]] = None
    command: Optional[List[str]] = None
    entrypoint: Optional[List[str]] = None
    working_dir: Optional[str] = None
    user: Optional[str] = None
    deploy_command: Optional[str] = None
    compose_file: Optional[str] = None
    compose_service: Optional[str] = None
    restart_policy: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ContainerListResponse(BaseModel):
    """Response schema for container list."""
    success: bool
    containers: List[Dict[str, Any]]
    total_count: int
    running_count: int
    stopped_count: int
    compose_projects: List[str]
    unique_images: List[str]
    total_size: Optional[str] = None
    error: Optional[str] = None


class ContainerOperationResponse(BaseModel):
    """Response schema for container operations."""
    success: bool
    container_name: str
    operation: str
    previous_status: Optional[ContainerStatus] = None
    current_status: Optional[ContainerStatus] = None
    message: str
    error: Optional[str] = None


class ContainerHealthResponse(BaseModel):
    """Response schema for container health check."""
    success: bool
    container_name: str
    health_status: HealthStatus
    error: Optional[str] = None


class ContainerLogsResponse(BaseModel):
    """Response schema for container logs."""
    success: bool
    container_name: str
    logs: List[str]
    total_lines: Optional[int] = None
    tail_lines: Optional[int] = None
    error: Optional[str] = None


class ContainerRemoveResponse(BaseModel):
    """Response schema for container removal."""
    success: bool
    container_name: str
    removed: bool
    force_used: bool
    message: str
    error: Optional[str] = None


class ContainerRedeployResponse(BaseModel):
    """Response schema for container redeployment."""
    success: bool
    container_name: str
    old_container_id: Optional[str] = None
    new_container_id: Optional[str] = None
    old_image: Optional[str] = None
    new_image: Optional[str] = None
    deploy_command: str
    message: str
    error: Optional[str] = None


__all__ = [
    "ContainerStatus",
    "HealthStatus",
    "DockerPsEntry",
    "DockerRequest",  # Legacy
    "DockerResponse",  # Legacy
    "ContainerNameRequest",
    "LogsRequest",
    "RemoveContainerRequest",
    "RedeployRequest",
    "ContainerInfoResponse",
    "ContainerListResponse",
    "ContainerOperationResponse",
    "ContainerHealthResponse",
    "ContainerLogsResponse",
    "ContainerRemoveResponse",
    "ContainerRedeployResponse",
]
