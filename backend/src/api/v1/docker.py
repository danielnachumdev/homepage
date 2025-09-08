from fastapi import APIRouter, HTTPException
from ...schemas.v1.docker import (
    ContainerNameRequest, LogsRequest, RemoveContainerRequest, RedeployRequest,
    ContainerInfoResponse, ContainerListResponse, ContainerOperationResponse,
    ContainerHealthResponse, ContainerLogsResponse, ContainerRemoveResponse,
    ContainerRedeployResponse
)
from ...services.v1.docker_service import DockerService

router = APIRouter(prefix="/docker", tags=["docker"])
docker_service = DockerService()


@router.get("/health/{container_name}", response_model=ContainerHealthResponse)
async def check_docker_health(container_name: str):
    """Check Docker container health"""
    result = await docker_service.health_check_container(container_name)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.get("/info/{container_name}", response_model=ContainerInfoResponse)
async def get_container_info(container_name: str):
    """Get detailed information about a Docker container"""
    result = await docker_service.get_container_info(container_name)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.get("/list", response_model=ContainerListResponse)
async def list_containers(all_containers: bool = False):
    """List all Docker containers"""
    result = await docker_service.list_containers(all_containers=all_containers)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.post("/start", response_model=ContainerOperationResponse)
async def start_container(request: ContainerNameRequest):
    """Start a Docker container"""
    result = await docker_service.start_container(request.container_name)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.post("/stop", response_model=ContainerOperationResponse)
async def stop_container(request: ContainerNameRequest):
    """Stop a Docker container"""
    result = await docker_service.stop_container(request.container_name)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.post("/restart", response_model=ContainerOperationResponse)
async def restart_container(request: ContainerNameRequest):
    """Restart a Docker container"""
    result = await docker_service.restart_container(request.container_name)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.post("/redeploy", response_model=ContainerRedeployResponse)
async def redeploy_container(request: RedeployRequest):
    """Redeploy a Docker container with new configuration"""
    result = await docker_service.redeploy_container(request)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.get("/logs/{container_name}", response_model=ContainerLogsResponse)
async def get_container_logs(container_name: str, tail_lines: int = 100):
    """Get logs from a Docker container"""
    result = await docker_service.get_container_logs(container_name, tail_lines)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.delete("/remove/{container_name}", response_model=ContainerRemoveResponse)
async def remove_container(container_name: str, force: bool = False):
    """Remove a Docker container"""
    result = await docker_service.remove_container(container_name, force)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


@router.post("/batch/stop", response_model=list[ContainerOperationResponse])
async def batch_stop_containers(container_names: list[str]):
    """Stop multiple Docker containers concurrently"""
    result = await docker_service.batch_container_operations(container_names, "stop")
    return result


@router.post("/batch/start", response_model=list[ContainerOperationResponse])
async def batch_start_containers(container_names: list[str]):
    """Start multiple Docker containers concurrently"""
    result = await docker_service.batch_container_operations(container_names, "start")
    return result


@router.post("/batch/restart", response_model=list[ContainerOperationResponse])
async def batch_restart_containers(container_names: list[str]):
    """Restart multiple Docker containers concurrently"""
    result = await docker_service.batch_container_operations(container_names, "restart")
    return result


__all__ = [
    "router"
]
