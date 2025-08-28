from typing import List, Optional
from ...gateways.v1.system_gateway import SystemGateway
from ...schemas.v1.docker import (
    ContainerNameRequest, LogsRequest, RemoveContainerRequest, RedeployRequest,
    ContainerInfoResponse, ContainerListResponse, ContainerOperationResponse,
    ContainerHealthResponse, ContainerLogsResponse, ContainerRemoveResponse,
    ContainerRedeployResponse, ContainerStatus, HealthStatus
)
from ...schemas.v1.system import CommandResponse


class DockerService:
    """Service for managing Docker containers using SystemGateway."""

    def __init__(self):
        self.system_gateway = SystemGateway()

    def get_container_info(self, container_name: str) -> ContainerInfoResponse:
        """Get detailed information about a specific Docker container."""
        try:
            # Get detailed container information using docker inspect
            command = f"docker inspect {container_name}"
            result = self.system_gateway.execute_command(command)

            if result.success:
                # Parse the inspect output to extract relevant information
                # For now, we'll return basic info - this can be enhanced with JSON parsing
                # In a real implementation, you'd parse the JSON output from docker inspect

                # Get additional container details
                image_command = f"docker inspect --format='{{{{.Config.Image}}}}' {container_name}"
                image_result = self.system_gateway.execute_command(
                    image_command)

                id_command = f"docker inspect --format='{{{{.Id}}}}' {container_name}"
                id_result = self.system_gateway.execute_command(id_command)

                status_command = f"docker inspect --format='{{{{.State.Status}}}}' {container_name}"
                status_result = self.system_gateway.execute_command(
                    status_command)

                # Build deploy command based on available information
                deploy_command = self._build_deploy_command(
                    container_name, image_result.output.strip() if image_result.success else None)

                return ContainerInfoResponse(
                    success=True,
                    container_name=container_name,
                    container_id=id_result.output.strip() if id_result.success else None,
                    status=self._parse_status(
                        status_result.output.strip() if status_result.success else None),
                    image=image_result.output.strip() if image_result.success else None,
                    image_id=None,  # Would extract from inspect output
                    created=None,  # Would extract from inspect output
                    ports=None,  # Would extract from inspect output
                    mounts=None,  # Would extract from inspect output
                    networks=None,  # Would extract from inspect output
                    health_status=None,  # Would extract from inspect output
                    environment_vars=None,  # Would extract from inspect output
                    command=None,  # Would extract from inspect output
                    entrypoint=None,  # Would extract from inspect output
                    working_dir=None,  # Would extract from inspect output
                    user=None,  # Would extract from inspect output
                    deploy_command=deploy_command,
                    compose_file=None,  # Would extract from inspect output
                    compose_service=None,  # Would extract from inspect output
                    restart_policy=None,  # Would extract from inspect output
                    error=None
                )
            else:
                return ContainerInfoResponse(
                    success=False,
                    container_name=container_name,
                    message=f"Failed to get container information for {container_name}",
                    error=result.error
                )
        except Exception as e:
            return ContainerInfoResponse(
                success=False,
                container_name=container_name,
                message=f"Error getting container information for {container_name}",
                error=str(e)
            )

    def _parse_status(self, status_str: Optional[str]) -> Optional[ContainerStatus]:
        """Parse container status string to ContainerStatus enum"""
        if not status_str:
            return None

        status_mapping = {
            "running": ContainerStatus.RUNNING,
            "stopped": ContainerStatus.STOPPED,
            "paused": ContainerStatus.PAUSED,
            "restarting": ContainerStatus.RESTARTING,
            "removing": ContainerStatus.REMOVING,
            "created": ContainerStatus.CREATED,
            "exited": ContainerStatus.EXITED,
            "dead": ContainerStatus.DEAD
        }

        return status_mapping.get(status_str.lower(), None)

    def _build_deploy_command(self, container_name: str, image: Optional[str]) -> str:
        """Build a docker run command for redeployment"""
        if not image:
            return f"docker run --name {container_name}"

        # Basic docker run command - in practice, you'd extract more details from inspect
        return f"docker run --name {container_name} {image}"

    def list_containers(self, all_containers: bool = False) -> ContainerListResponse:
        """List all Docker containers."""
        try:
            flag = "-a" if all_containers else ""
            command = f"docker ps {flag}".strip()
            result = self.system_gateway.execute_command(command)

            if result.success:
                # Parse the ps output to extract container information
                containers = []
                lines = result.output.strip().split('\n')[1:]  # Skip header
                running_count = 0
                stopped_count = 0

                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 7:
                            container_info = {
                                "id": parts[0],
                                "image": parts[1],
                                "command": parts[2],
                                "created": parts[3],
                                "status": parts[4],
                                "ports": parts[5],
                                "names": parts[6]
                            }
                            containers.append(container_info)

                            if "Up" in parts[4]:
                                running_count += 1
                            else:
                                stopped_count += 1

                return ContainerListResponse(
                    success=True,
                    containers=containers,
                    total_count=len(containers),
                    running_count=running_count,
                    stopped_count=stopped_count,
                    error=None
                )
            else:
                return ContainerListResponse(
                    success=False,
                    containers=[],
                    error=result.error
                )
        except Exception as e:
            return ContainerListResponse(
                success=False,
                containers=[],
                error=str(e)
            )

    def stop_container(self, container_name: str) -> ContainerOperationResponse:
        """Stop a running Docker container by name."""
        try:
            command = f"docker stop {container_name}"
            result = self.system_gateway.execute_command(command)

            if result.success:
                return ContainerOperationResponse(
                    success=True,
                    container_name=container_name,
                    operation="stop",
                    previous_status=ContainerStatus.RUNNING,
                    current_status=ContainerStatus.STOPPED,
                    message=f"Container {container_name} stopped successfully",
                    error=None
                )
            else:
                return ContainerOperationResponse(
                    success=False,
                    container_name=container_name,
                    operation="stop",
                    message=f"Failed to stop container {container_name}",
                    error=result.error
                )
        except Exception as e:
            return ContainerOperationResponse(
                success=False,
                container_name=container_name,
                operation="stop",
                message=f"Error stopping container {container_name}",
                error=str(e)
            )

    def start_container(self, container_name: str) -> ContainerOperationResponse:
        """Start a stopped Docker container by name."""
        try:
            command = f"docker start {container_name}"
            result = self.system_gateway.execute_command(command)

            if result.success:
                return ContainerOperationResponse(
                    success=True,
                    container_name=container_name,
                    operation="start",
                    previous_status=ContainerStatus.STOPPED,
                    current_status=ContainerStatus.RUNNING,
                    message=f"Container {container_name} started successfully",
                    error=None
                )
            else:
                return ContainerOperationResponse(
                    success=False,
                    container_name=container_name,
                    operation="start",
                    message=f"Failed to start container {container_name}",
                    error=result.error
                )
        except Exception as e:
            return ContainerOperationResponse(
                success=False,
                container_name=container_name,
                operation="start",
                message=f"Error starting container {container_name}",
                error=str(e)
            )

    def restart_container(self, container_name: str) -> ContainerOperationResponse:
        """Restart a Docker container by name."""
        try:
            command = f"docker restart {container_name}"
            result = self.system_gateway.execute_command(command)

            if result.success:
                return ContainerOperationResponse(
                    success=True,
                    container_name=container_name,
                    operation="restart",
                    previous_status=ContainerStatus.RUNNING,
                    current_status=ContainerStatus.RUNNING,
                    message=f"Container {container_name} restarted successfully",
                    error=None
                )
            else:
                return ContainerOperationResponse(
                    success=False,
                    container_name=container_name,
                    operation="restart",
                    message=f"Failed to restart container {container_name}",
                    error=result.error
                )
        except Exception as e:
            return ContainerOperationResponse(
                success=False,
                container_name=container_name,
                operation="restart",
                message=f"Error restarting container {container_name}",
                error=str(e)
            )

    def health_check_container(self, container_name: str) -> ContainerHealthResponse:
        """Check the health status of a Docker container."""
        try:
            # First check if container exists and get its status
            inspect_command = f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}"
            result = self.system_gateway.execute_command(inspect_command)

            if result.success:
                health_status_str = result.output.strip()
                if health_status_str:
                    # Map the health status to our enum
                    if health_status_str == "healthy":
                        health_status = HealthStatus.HEALTHY
                    elif health_status_str == "unhealthy":
                        health_status = HealthStatus.UNHEALTHY
                    elif health_status_str == "starting":
                        health_status = HealthStatus.STARTING
                    else:
                        health_status = HealthStatus.NONE

                    return ContainerHealthResponse(
                        success=True,
                        container_name=container_name,
                        health_status=health_status,
                        error=None
                    )
                else:
                    # Container exists but no health check configured
                    return ContainerHealthResponse(
                        success=True,
                        container_name=container_name,
                        health_status=HealthStatus.NONE,
                        error=None
                    )
            else:
                return ContainerHealthResponse(
                    success=False,
                    container_name=container_name,
                    health_status=HealthStatus.NONE,
                    error=result.error
                )
        except Exception as e:
            return ContainerHealthResponse(
                success=False,
                container_name=container_name,
                health_status=HealthStatus.NONE,
                error=str(e)
            )

    def get_container_logs(self, container_name: str, tail_lines: int = 100) -> ContainerLogsResponse:
        """Get recent logs from a Docker container."""
        try:
            command = f"docker logs --tail {tail_lines} {container_name}"
            result = self.system_gateway.execute_command(command)

            if result.success:
                logs = result.output.strip().split('\n') if result.output.strip() else []
                return ContainerLogsResponse(
                    success=True,
                    container_name=container_name,
                    logs=logs,
                    total_lines=len(logs),
                    tail_lines=tail_lines,
                    error=None
                )
            else:
                return ContainerLogsResponse(
                    success=False,
                    container_name=container_name,
                    logs=[],
                    error=result.error
                )
        except Exception as e:
            return ContainerLogsResponse(
                success=False,
                container_name=container_name,
                logs=[],
                error=str(e)
            )

    def remove_container(self, container_name: str, force: bool = False) -> ContainerRemoveResponse:
        """Remove a Docker container by name."""
        try:
            flag = "-f" if force else ""
            command = f"docker rm {flag} {container_name}".strip()
            result = self.system_gateway.execute_command(command)

            if result.success:
                return ContainerRemoveResponse(
                    success=True,
                    container_name=container_name,
                    removed=True,
                    force_used=force,
                    message=f"Container {container_name} removed successfully",
                    error=None
                )
            else:
                return ContainerRemoveResponse(
                    success=False,
                    container_name=container_name,
                    removed=False,
                    force_used=force,
                    message=f"Failed to remove container {container_name}",
                    error=result.error
                )
        except Exception as e:
            return ContainerRemoveResponse(
                success=False,
                container_name=container_name,
                removed=False,
                force_used=force,
                message=f"Error removing container {container_name}",
                error=str(e)
            )

    def redeploy_container(self, request: RedeployRequest) -> ContainerRedeployResponse:
        """Redeploy a container with new configuration."""
        try:
            # Get current container info
            current_info = self.get_container_info(request.container_name)
            if not current_info.success:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    deploy_command="",
                    message=f"Failed to get current container info: {current_info.error}",
                    error=current_info.error
                )

            old_container_id = current_info.container_id
            old_image = current_info.image
            new_image = request.image or old_image

            if not new_image:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    deploy_command="",
                    message="No image specified and no current image found",
                    error="Missing image information"
                )

            # Stop and remove the old container
            stop_result = self.stop_container(request.container_name)
            if not stop_result.success:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    deploy_command="",
                    message=f"Failed to stop container: {stop_result.error}",
                    error=stop_result.error
                )

            remove_result = self.remove_container(
                request.container_name, force=True)
            if not remove_result.success:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    deploy_command="",
                    message=f"Failed to remove container: {remove_result.error}",
                    error=remove_result.error
                )

            # Build the new deploy command
            deploy_command = self._build_redeploy_command(request, new_image)

            # Run the new container
            run_result = self.system_gateway.execute_command(deploy_command)
            if not run_result.success:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    old_container_id=old_container_id,
                    old_image=old_image,
                    new_image=new_image,
                    deploy_command=deploy_command,
                    message=f"Failed to start new container: {run_result.error}",
                    error=run_result.error
                )

            # Get the new container ID
            new_id_result = self.system_gateway.execute_command(
                f"docker inspect --format='{{{{.Id}}}}' {request.container_name}")
            new_container_id = new_id_result.output.strip() if new_id_result.success else None

            return ContainerRedeployResponse(
                success=True,
                container_name=request.container_name,
                old_container_id=old_container_id,
                new_container_id=new_container_id,
                old_image=old_image,
                new_image=new_image,
                deploy_command=deploy_command,
                message=f"Container {request.container_name} redeployed successfully",
                error=None
            )

        except Exception as e:
            return ContainerRedeployResponse(
                success=False,
                container_name=request.container_name,
                deploy_command="",
                message=f"Error redeploying container: {str(e)}",
                error=str(e)
            )

    def _build_redeploy_command(self, request: RedeployRequest, image: str) -> str:
        """Build the docker run command for redeployment"""
        cmd_parts = ["docker", "run", "-d"]  # -d for detached mode

        # Container name
        cmd_parts.extend(["--name", request.container_name])

        # Environment variables
        if request.environment_vars:
            for key, value in request.environment_vars.items():
                cmd_parts.extend(["-e", f"{key}={value}"])

        # Port mappings
        if request.ports:
            for host_port, container_port in request.ports.items():
                cmd_parts.extend(["-p", f"{host_port}:{container_port}"])

        # Volume mounts
        if request.volumes:
            for volume in request.volumes:
                cmd_parts.extend(["-v", volume])

        # Image
        cmd_parts.append(image)

        return " ".join(cmd_parts)


__all__ = [
    "DockerService"
]
