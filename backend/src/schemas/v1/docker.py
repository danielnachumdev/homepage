from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class ContainerStatus(str, Enum):
    """Container status enumeration"""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    CREATED = "created"
    EXITED = "exited"
    DEAD = "dead"


class HealthStatus(str, Enum):
    """Container health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    NONE = "none"


# Base request schemas
class ContainerNameRequest(BaseModel):
    """Base request for operations that need a container name"""
    container_name: str


class LogsRequest(BaseModel):
    """Request for getting container logs"""
    container_name: str
    tail_lines: int = 100
    follow: bool = False


class RemoveContainerRequest(BaseModel):
    """Request for removing a container"""
    container_name: str
    force: bool = False


class RedeployRequest(BaseModel):
    """Request for redeploying a container"""
    container_name: str
    image: Optional[str] = None  # If not provided, use current image
    force_rebuild: bool = False
    environment_vars: Optional[Dict[str, str]] = None
    ports: Optional[Dict[str, str]] = None
    volumes: Optional[List[str]] = None


# Response schemas for specific operations
class ContainerInfoResponse(BaseModel):
    """Response for container information"""
    success: bool
    container_name: str
    container_id: Optional[str] = None
    status: Optional[ContainerStatus] = None
    image: Optional[str] = None
    image_id: Optional[str] = None
    created: Optional[str] = None
    ports: Optional[List[str]] = None
    mounts: Optional[List[str]] = None
    networks: Optional[List[str]] = None
    health_status: Optional[HealthStatus] = None
    environment_vars: Optional[Dict[str, str]] = None
    command: Optional[str] = None
    entrypoint: Optional[str] = None
    working_dir: Optional[str] = None
    user: Optional[str] = None
    # Redeployment information
    deploy_command: Optional[str] = None
    compose_file: Optional[str] = None
    compose_service: Optional[str] = None
    restart_policy: Optional[str] = None
    error: Optional[str] = None


class ContainerListResponse(BaseModel):
    """Response for listing containers"""
    success: bool
    containers: List[Dict[str, Any]] = []
    total_count: int = 0
    running_count: int = 0
    stopped_count: int = 0
    error: Optional[str] = None


class ContainerOperationResponse(BaseModel):
    """Response for container operations (start, stop, restart)"""
    success: bool
    container_name: str
    operation: str
    previous_status: Optional[ContainerStatus] = None
    current_status: Optional[ContainerStatus] = None
    message: str
    error: Optional[str] = None


class ContainerHealthResponse(BaseModel):
    """Response for container health check"""
    success: bool
    container_name: str
    health_status: HealthStatus
    last_check: Optional[str] = None
    failure_count: Optional[int] = None
    log: Optional[List[str]] = None
    error: Optional[str] = None


class ContainerLogsResponse(BaseModel):
    """Response for container logs"""
    success: bool
    container_name: str
    logs: List[str] = []
    total_lines: int = 0
    tail_lines: int = 100
    error: Optional[str] = None


class ContainerRemoveResponse(BaseModel):
    """Response for container removal"""
    success: bool
    container_name: str
    removed: bool = False
    force_used: bool = False
    message: str
    error: Optional[str] = None


class ContainerRedeployResponse(BaseModel):
    """Response for container redeployment"""
    success: bool
    container_name: str
    old_container_id: Optional[str] = None
    new_container_id: Optional[str] = None
    old_image: Optional[str] = None
    new_image: Optional[str] = None
    deploy_command: str
    message: str
    error: Optional[str] = None


# Legacy schemas for backward compatibility (can be removed later)
class DockerRequest(BaseModel):
    """Legacy request schema - deprecated"""
    container_name: str


class DockerResponse(BaseModel):
    """Legacy response schema - deprecated"""
    success: bool
    message: str
    error: Optional[str] = None


__all__ = [
    "ContainerStatus",
    "HealthStatus",
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
    "DockerRequest",  # Legacy
    "DockerResponse"  # Legacy
]
