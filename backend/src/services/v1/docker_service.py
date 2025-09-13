from typing import List, Optional
from ...utils.command import AsyncCommand, CommandType
from ...schemas.v1.docker import (
    ContainerNameRequest, LogsRequest, RemoveContainerRequest, RedeployRequest,
    ContainerInfoResponse, ContainerListResponse, ContainerOperationResponse,
    ContainerHealthResponse, ContainerLogsResponse, ContainerRemoveResponse,
    ContainerRedeployResponse, ContainerStatus, HealthStatus, DockerPsEntry
)
from ...utils.logger import get_logger
import asyncio


class DockerService:
    """Service for managing Docker containers using AsyncCommand."""

    def __init__(self):
        self.logger = get_logger("DockerService")

    async def get_container_info(self, container_name: str) -> ContainerInfoResponse:
        """Get detailed information about a specific Docker container."""
        self.logger.info("Getting container info for: %s", container_name)

        try:
            # Get detailed container information using docker inspect with JSON format
            command = f"docker inspect {container_name} --format json"
            self.logger.debug("Executing command: %s", command)
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

            if result.success:
                self.logger.debug("Successfully executed docker inspect command")
                try:
                    import json
                    container_data = json.loads(result.stdout)
                    self.logger.debug("Successfully parsed container data JSON")

                    # Extract all the rich information from the inspect output
                    container_id = container_data.get("Id", "")
                    image = container_data.get("Config", {}).get("Image", "")
                    image_id = container_data.get("Image", "")
                    created = container_data.get("Created", "")
                    state = container_data.get("State", {})
                    status = state.get("Status", "")
                    health_status = state.get("Health", {}).get("Status") if state.get("Health") else None

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
                            "read_only": mount.get("RW", True)
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

                    # Extract command and entrypoint
                    command = container_data.get("Config", {}).get("Cmd", [])
                    entrypoint = container_data.get("Config", {}).get("Entrypoint", [])
                    working_dir = container_data.get("Config", {}).get("WorkingDir", "")
                    user = container_data.get("Config", {}).get("User", "")

                    # Extract compose information from labels
                    labels = container_data.get("Config", {}).get("Labels", {})
                    compose_info = self._parse_compose_labels_from_dict(labels)

                    # Build deploy command based on available information
                    deploy_command = self._build_deploy_command_from_inspect(container_data)

                    self.logger.info("Successfully retrieved container info for: %s", container_name)
                    return ContainerInfoResponse(
                        success=True,
                        container_name=container_name,
                        container_id=container_id,
                        status=self._parse_status(status),
                        image=image,
                        image_id=image_id,
                        created=created,
                        ports=ports,
                        mounts=mounts,
                        networks=networks,
                        health_status=self._parse_health_status(health_status),
                        environment_vars=env_vars,
                        command=command,
                        entrypoint=entrypoint,
                        working_dir=working_dir,
                        user=user,
                        deploy_command=deploy_command,
                        compose_file=compose_info.get("config_files"),
                        compose_service=compose_info.get("service"),
                        restart_policy=container_data.get("HostConfig", {}).get("RestartPolicy", {}).get("Name"),
                        error=None
                    )

                except json.JSONDecodeError as e:
                    self.logger.error("Failed to parse container JSON for %s: %s", container_name, str(e))
                    return ContainerInfoResponse(
                        success=False,
                        container_name=container_name,
                        message=f"Failed to parse container information: {str(e)}",
                        error=f"JSON decode error: {str(e)}"
                    )
            else:
                self.logger.error("Failed to execute docker inspect for %s: %s", container_name, result.stderr)
                return ContainerInfoResponse(
                    success=False,
                    container_name=container_name,
                    message=f"Failed to get container information for {container_name}",
                    error=result.stderr
                )
        except Exception as e:
            self.logger.error("Error getting container info for %s: %s", container_name, str(e))
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

    def _parse_compose_labels_from_dict(self, labels: dict) -> dict:
        """Parse docker-compose labels from a dictionary"""
        compose_info = {}

        for key, value in labels.items():
            if key.startswith('com.docker.compose.'):
                if key == 'com.docker.compose.project':
                    compose_info['project'] = value
                elif key == 'com.docker.compose.service':
                    compose_info['service'] = value
                elif key == 'com.docker.compose.config-hash':
                    compose_info['config_hash'] = value
                elif key == 'com.docker.compose.container-number':
                    compose_info['container_number'] = value
                elif key == 'com.docker.compose.depends_on':
                    compose_info['depends_on'] = value
                elif key == 'com.docker.compose.version':
                    compose_info['version'] = value
                elif key == 'com.docker.compose.project.config_files':
                    compose_info['config_files'] = value
                elif key == 'com.docker.compose.project.working_dir':
                    compose_info['working_dir'] = value

        return compose_info

    def _parse_health_status(self, health_status: Optional[str]) -> Optional[HealthStatus]:
        """Parse health status string to HealthStatus enum"""
        if not health_status:
            return None

        status_mapping = {
            "healthy": HealthStatus.HEALTHY,
            "unhealthy": HealthStatus.UNHEALTHY,
            "starting": HealthStatus.STARTING,
            "none": HealthStatus.NONE
        }

        return status_mapping.get(health_status.lower(), HealthStatus.NONE)

    def _build_deploy_command(self, container_name: str, image: Optional[str]) -> str:
        """Build a docker run command for redeployment"""
        if not image:
            return f"docker run --name {container_name}"

        # Basic docker run command - in practice, you'd extract more details from inspect
        return f"docker run --name {container_name} {image}"

    def _build_deploy_command_from_inspect(self, container_data: dict) -> str:
        """Build a comprehensive docker run command from inspect data"""
        cmd_parts = ["docker", "run", "-d"]

        # Container name
        name = container_data.get("Name", "").lstrip('/')
        if name:
            cmd_parts.extend(["--name", name])

        # Image
        image = container_data.get("Config", {}).get("Image", "")
        if image:
            cmd_parts.append(image)

        # Ports
        network_settings = container_data.get("NetworkSettings", {})
        if "Ports" in network_settings:
            for port_binding, host_bindings in network_settings["Ports"].items():
                if host_bindings:
                    for host_binding in host_bindings:
                        host_ip = host_binding.get("HostIp", "")
                        host_port = host_binding.get("HostPort", "")
                        if host_ip and host_ip != "0.0.0.0":
                            cmd_parts.extend(["-p", f"{host_ip}:{host_port}:{port_binding}"])
                        else:
                            cmd_parts.extend(["-p", f"{host_port}:{port_binding}"])

        # Volumes
        for mount in container_data.get("Mounts", []):
            mount_type = mount.get("Type", "")
            if mount_type == "bind":
                source = mount.get("Source", "")
                destination = mount.get("Destination", "")
                read_only = mount.get("RW", True)
                if source and destination:
                    ro_flag = ":ro" if not read_only else ""
                    cmd_parts.extend(["-v", f"{source}:{destination}{ro_flag}"])
            elif mount_type == "volume":
                source = mount.get("Name", "")
                destination = mount.get("Destination", "")
                if source and destination:
                    cmd_parts.extend(["-v", f"{source}:{destination}"])

        # Environment variables
        for env in container_data.get("Config", {}).get("Env", []):
            if '=' in env:
                cmd_parts.extend(["-e", env])

        # Working directory
        working_dir = container_data.get("Config", {}).get("WorkingDir", "")
        if working_dir:
            cmd_parts.extend(["-w", working_dir])

        # User
        user = container_data.get("Config", {}).get("User", "")
        if user:
            cmd_parts.extend(["-u", user])

        # Restart policy
        restart_policy = container_data.get("HostConfig", {}).get(
            "RestartPolicy", {}).get("Name", "")
        if restart_policy and restart_policy != "no":
            cmd_parts.extend(["--restart", restart_policy])

        return " ".join(cmd_parts)

    async def list_containers(self, all_containers: bool = False) -> ContainerListResponse:
        """List all Docker containers."""
        self.logger.info("Listing containers (all_containers=%s)", all_containers)

        try:
            flag = "-a" if all_containers else ""
            command = f"docker ps {flag} --format json"
            self.logger.debug("Executing command: %s", command)
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

            if result.success:
                self.logger.debug("Successfully executed docker ps command")
                # Parse JSON output for each container
                docker_entries = []
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            import json
                            container_data = json.loads(line)
                            docker_entries.append(DockerPsEntry(**container_data))
                        except json.JSONDecodeError as e:
                            # Handle cases where line might not be a valid JSON object
                            # For example, if it's a header or an error message
                            pass

                # Filter out any non-container lines (like headers or errors)
                docker_entries = [
                    c for c in docker_entries if c.ID and c.Image and c.Command and c.CreatedAt and c.Status
                ]

                # Track summary information
                compose_projects = set()
                unique_images = set()
                total_size_bytes = 0
                running_count = 0
                stopped_count = 0

                # Convert to response format
                containers = []

                # Get container details concurrently for better performance
                container_details_tasks = [
                    self._get_container_details(container.ID, container.Names)
                    for container in docker_entries
                ]
                container_details_results = await asyncio.gather(*container_details_tasks, return_exceptions=True)

                for i, container in enumerate(docker_entries):
                    # Get container details (handle any exceptions)
                    container_details = {}
                    if i < len(container_details_results):
                        result = container_details_results[i]
                        if isinstance(result, Exception):
                            # If getting details failed, continue with basic info
                            pass
                        else:
                            container_details = result

                    # Parse compose information from labels
                    compose_info = self._parse_compose_labels(container.Labels)

                    container_info = {
                        "id": container.ID,
                        "image": container.Image,
                        "command": container.Command,
                        "created": container.CreatedAt,
                        "state": container.State,
                        "status": container.Status,
                        "ports": container.Ports,
                        "names": container.Names,
                        "running_for": container.RunningFor,
                        "size": container.Size,
                        # Additional details from inspect
                        "container_name": container_details.get("name", container.Names),
                        "compose_project": container_details.get("compose_project"),
                        "compose_service": container_details.get("compose_service"),
                        "image_tag": container_details.get("image_tag"),
                        "health_status": container_details.get("health_status"),
                        "mounts": container_details.get("mounts"),
                        "networks": container_details.get("networks"),
                        # Rich data from JSON format
                        "labels": container.Labels,
                        "local_volumes": container.LocalVolumes,
                        "platform": {
                            "architecture": container.Platform.architecture,
                            "os": container.Platform.os
                        },
                        # Compose information from labels
                        "compose_project": compose_info.get("project"),
                        "compose_service": compose_info.get("service"),
                        "compose_config_hash": compose_info.get("config_hash"),
                        "compose_container_number": compose_info.get("container_number"),
                        "compose_depends_on": compose_info.get("depends_on"),
                        "compose_version": compose_info.get("version"),
                        "compose_config_files": compose_info.get("config_files"),
                        "compose_working_dir": compose_info.get("working_dir")
                    }
                    containers.append(container_info)

                    # Update summary information
                    if compose_info.get("project"):
                        compose_projects.add(compose_info["project"])
                    if container.Image:
                        unique_images.add(container.Image)
                    if container_details.get("size"):
                        # Try to parse size for total calculation
                        size_str = container_details["size"]
                        try:
                            if "KB" in size_str:
                                total_size_bytes += float(
                                    size_str.replace(" KB", "")) * 1024
                            elif "MB" in size_str:
                                total_size_bytes += float(
                                    size_str.replace(" MB", "")) * 1024 * 1024
                            elif "GB" in size_str:
                                total_size_bytes += float(
                                    size_str.replace(" GB", "")) * 1024 * 1024 * 1024
                            elif "B" in size_str and "KB" not in size_str and "MB" not in size_str and "GB" not in size_str:
                                total_size_bytes += float(
                                    size_str.replace(" B", ""))
                        except ValueError:
                            pass

                    if container.State == "running":
                        running_count += 1
                    else:
                        stopped_count += 1

                self.logger.info("Successfully listed %d containers (%d running, %d stopped)",
                                 len(containers), running_count, stopped_count)
                return ContainerListResponse(
                    success=True,
                    containers=containers,
                    total_count=len(containers),
                    running_count=running_count,
                    stopped_count=stopped_count,
                    compose_projects=list(compose_projects),
                    unique_images=list(unique_images),
                    total_size=None,  # Size is per-container in JSON format
                    error=None
                )
            else:
                self.logger.error("Failed to execute docker ps command: %s", result.stderr)
                return ContainerListResponse(
                    success=False,
                    containers=[],
                    error=result.stderr
                )
        except Exception as e:
            self.logger.error("Error listing containers: %s", str(e))
            return ContainerListResponse(
                success=False,
                containers=[],
                error=str(e)
            )

    async def _get_container_details(self, container_id: str, names: str) -> dict:
        """Get additional container details using docker inspect"""
        details = {}

        try:
            # Get container name (first name if multiple)
            container_names = names.split(',')
            details["name"] = container_names[0].strip()

            # Check if this is a compose container
            if len(container_names) > 1:
                # Look for compose project and service names
                for name in container_names:
                    name = name.strip()
                    if '_' in name and name.count('_') >= 2:
                        # Typical compose naming: project_service_number
                        parts = name.split('_')
                        if len(parts) >= 2:
                            details["compose_project"] = parts[0]
                            details["compose_service"] = parts[1]
                            break

            # Get additional details using docker inspect
            inspect_command = f"docker inspect {container_id}"
            inspect_cmd = AsyncCommand.cmd(inspect_command)
            inspect_result = await inspect_cmd.execute()

            if inspect_result.success:
                # Extract image tag
                image_tag_cmd = f"docker inspect --format='{{{{.Config.Image}}}}' {container_id}"
                image_cmd = AsyncCommand.cmd(image_tag_cmd)
                image_result = await image_cmd.execute()
                if image_result.success:
                    details["image_tag"] = image_result.stdout.strip()

                # Extract health status
                health_cmd = f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_id}"
                health_async_cmd = AsyncCommand.cmd(health_cmd)
                health_result = await health_async_cmd.execute()
                if health_result.success and health_result.stdout.strip():
                    details["health_status"] = health_result.stdout.strip()

                # Extract size information
                size_cmd = f"docker inspect --format='{{{{.Size}}}}' {container_id}"
                size_async_cmd = AsyncCommand.cmd(size_cmd)
                size_result = await size_async_cmd.execute()
                if size_result.success:
                    try:
                        size_bytes = int(size_result.stdout.strip())
                        details["size"] = self._format_size(size_bytes)
                    except ValueError:
                        details["size"] = size_result.stdout.strip()

                # Extract mount information
                mounts_cmd = f"docker inspect --format='{{{{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}}}' {container_id}"
                mounts_async_cmd = AsyncCommand.cmd(mounts_cmd)
                mounts_result = await mounts_async_cmd.execute()
                if mounts_result.success and mounts_result.stdout.strip():
                    details["mounts"] = mounts_result.stdout.strip().split()

                # Extract network information
                networks_cmd = f"docker inspect --format='{{{{range $key, $value := .NetworkSettings.Networks}}{{$key}} {{end}}}}' {container_id}"
                networks_async_cmd = AsyncCommand.cmd(networks_cmd)
                networks_result = await networks_async_cmd.execute()
                if networks_result.success and networks_result.stdout.strip():
                    details["networks"] = networks_result.stdout.strip().split()

        except Exception as e:
            # If we can't get details, just continue with basic info
            pass

        return details

    def _parse_compose_labels(self, labels_str: str) -> dict:
        """Parse docker-compose labels to extract project and service information"""
        compose_info = {}

        if not labels_str:
            return compose_info

        # Split labels by comma and parse each one
        labels = labels_str.split(',')
        for label in labels:
            label = label.strip()
            if label.startswith('com.docker.compose.'):
                # Extract compose information
                if 'project=' in label:
                    compose_info['project'] = label.split('=')[1]
                elif 'service=' in label:
                    compose_info['service'] = label.split('=')[1]
                elif 'config-hash=' in label:
                    compose_info['config_hash'] = label.split('=')[1]
                elif 'container-number=' in label:
                    compose_info['container_number'] = label.split('=')[1]
                elif 'depends_on=' in label:
                    compose_info['depends_on'] = label.split('=')[1]
                elif 'version=' in label:
                    compose_info['version'] = label.split('=')[1]
                elif 'config_files=' in label:
                    compose_info['config_files'] = label.split('=')[1]
                elif 'working_dir=' in label:
                    compose_info['working_dir'] = label.split('=')[1]

        return compose_info

    def _parse_ports(self, ports_str: str) -> list:
        """Parse ports string into structured format"""
        if not ports_str:
            return []

        ports = []
        # Handle multiple port mappings
        port_mappings = ports_str.split(', ')
        for mapping in port_mappings:
            if '->' in mapping:
                # Format: "0.0.0.0:8080->8010/tcp"
                parts = mapping.split('->')
                if len(parts) == 2:
                    host_part = parts[0].strip()
                    container_part = parts[1].strip()

                    # Extract host and container ports
                    host_port = host_part.split(
                        ':')[1] if ':' in host_part else host_part
                    container_port = container_part.split('/')[0]
                    protocol = container_part.split(
                        '/')[1] if '/' in container_part else 'tcp'

                    ports.append({
                        "host": host_part,
                        "container": container_part,
                        "host_port": host_port,
                        "container_port": container_port,
                        "protocol": protocol
                    })
            else:
                # Single port without mapping
                ports.append({"port": mapping.strip()})

        return ports

    def _parse_mounts(self, mounts_str: str) -> list:
        """Parse mounts string into structured format"""
        if not mounts_str:
            return []

        mounts = []
        # Handle multiple mounts
        mount_list = mounts_str.split(', ')
        for mount in mount_list:
            if ':' in mount:
                # Format: "source:target"
                parts = mount.split(':')
                if len(parts) >= 2:
                    source = parts[0]
                    target = ':'.join(parts[1:])  # Handle paths with colons
                    mounts.append({
                        "source": source,
                        "target": target
                    })
            else:
                # Named volume
                mounts.append({"volume": mount})

        return mounts

    def _parse_networks(self, networks_str: str) -> list:
        """Parse networks string into list"""
        if not networks_str:
            return []

        # Networks are comma-separated
        return [network.strip() for network in networks_str.split(',')]

    def _parse_labels(self, labels_str: str) -> dict:
        """Parse all labels into a dictionary"""
        labels = {}

        if not labels_str:
            return labels

        # Split labels by comma and parse each one
        label_pairs = labels_str.split(',')
        for label_pair in label_pairs:
            label_pair = label_pair.strip()
            if '=' in label_pair:
                key, value = label_pair.split('=', 1)
                labels[key.strip()] = value.strip()

        return labels

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    async def stop_container(self, container_name: str) -> ContainerOperationResponse:
        """Stop a running Docker container by name."""
        self.logger.info("Stopping container: %s", container_name)

        try:
            command = f"docker stop {container_name}"
            self.logger.debug("Executing command: %s", command)
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

            if result.success:
                self.logger.info("Successfully stopped container: %s", container_name)
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
                self.logger.error("Failed to stop container %s: %s", container_name, result.stderr)
                return ContainerOperationResponse(
                    success=False,
                    container_name=container_name,
                    operation="stop",
                    message=f"Failed to stop container {container_name}",
                    error=result.stderr
                )
        except Exception as e:
            self.logger.error("Error stopping container %s: %s", container_name, str(e))
            return ContainerOperationResponse(
                success=False,
                container_name=container_name,
                operation="stop",
                message=f"Error stopping container {container_name}",
                error=str(e)
            )

    async def start_container(self, container_name: str) -> ContainerOperationResponse:
        """Start a stopped Docker container by name."""
        self.logger.info("Starting container: %s", container_name)

        try:
            command = f"docker start {container_name}"
            self.logger.debug("Executing command: %s", command)
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

            if result.success:
                self.logger.info("Successfully started container: %s", container_name)
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
                self.logger.error("Failed to start container %s: %s", container_name, result.stderr)
                return ContainerOperationResponse(
                    success=False,
                    container_name=container_name,
                    operation="start",
                    message=f"Failed to start container {container_name}",
                    error=result.stderr
                )
        except Exception as e:
            self.logger.error("Error starting container %s: %s", container_name, str(e))
            return ContainerOperationResponse(
                success=False,
                container_name=container_name,
                operation="start",
                message=f"Error starting container {container_name}",
                error=str(e)
            )

    async def restart_container(self, container_name: str) -> ContainerOperationResponse:
        """Restart a Docker container by name."""
        try:
            command = f"docker restart {container_name}"
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

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
                    error=result.stderr
                )
        except Exception as e:
            return ContainerOperationResponse(
                success=False,
                container_name=container_name,
                operation="restart",
                message=f"Error restarting container {container_name}",
                error=str(e)
            )

    async def health_check_container(self, container_name: str) -> ContainerHealthResponse:
        """Check the health status of a Docker container."""
        try:
            # First check if container exists and get its status
            inspect_command = f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}"
            async_cmd = AsyncCommand.cmd(inspect_command)
            result = await async_cmd.execute()

            if result.success:
                health_status_str = result.stdout.strip()
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
                    error=result.stderr
                )
        except Exception as e:
            return ContainerHealthResponse(
                success=False,
                container_name=container_name,
                health_status=HealthStatus.NONE,
                error=str(e)
            )

    async def get_container_logs(self, container_name: str, tail_lines: int = 100) -> ContainerLogsResponse:
        """Get recent logs from a Docker container."""
        try:
            command = f"docker logs --tail {tail_lines} {container_name}"
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

            if result.success:
                logs = result.stdout.strip().split('\n') if result.stdout.strip() else []
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
                    error=result.stderr
                )
        except Exception as e:
            return ContainerLogsResponse(
                success=False,
                container_name=container_name,
                logs=[],
                error=str(e)
            )

    async def remove_container(self, container_name: str, force: bool = False) -> ContainerRemoveResponse:
        """Remove a Docker container by name."""
        try:
            flag = "-f" if force else ""
            command = f"docker rm {flag} {container_name}".strip()
            async_cmd = AsyncCommand.cmd(command)
            result = await async_cmd.execute()

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
                    error=result.stderr
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

    async def redeploy_container(self, request: RedeployRequest) -> ContainerRedeployResponse:
        """Redeploy a container with new configuration."""
        try:
            # Get current container info
            current_info = await self.get_container_info(request.container_name)
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
            stop_result = await self.stop_container(request.container_name)
            if not stop_result.success:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    deploy_command="",
                    message=f"Failed to stop container: {stop_result.error}",
                    error=stop_result.error
                )

            remove_result = await self.remove_container(
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
            run_async_cmd = AsyncCommand.cmd(deploy_command)
            run_result = await run_async_cmd.execute()
            if not run_result.success:
                return ContainerRedeployResponse(
                    success=False,
                    container_name=request.container_name,
                    old_container_id=old_container_id,
                    old_image=old_image,
                    new_image=new_image,
                    deploy_command=deploy_command,
                    message=f"Failed to start new container: {run_result.stderr}",
                    error=run_result.stderr
                )

            # Get the new container ID
            new_id_async_cmd = AsyncCommand.cmd(f"docker inspect --format='{{{{.Id}}}}' {request.container_name}")
            new_id_result = await new_id_async_cmd.execute()
            new_container_id = new_id_result.stdout.strip() if new_id_result.success else None

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

    async def execute_multiple_commands(self, commands: list[str]) -> list:
        """Execute multiple Docker commands concurrently for better performance."""
        # Create AsyncCommand instances for all commands
        async_commands = [AsyncCommand.cmd(cmd) for cmd in commands]

        # Execute all commands concurrently
        tasks = [cmd.execute() for cmd in async_commands]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert results to a simple format
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append({
                    'success': False,
                    'output': '',
                    'error': str(result)
                })
            else:
                responses.append({
                    'success': result.success,
                    'output': result.stdout,
                    'error': result.stderr if not result.success else None
                })

        return responses

    async def batch_container_operations(self, container_names: list[str], operation: str) -> list[
        ContainerOperationResponse]:
        """Execute the same operation on multiple containers concurrently."""
        self.logger.info("Starting batch %s operation on %d containers: %s",
                         operation, len(container_names), container_names)

        if operation == "stop":
            commands = [f"docker stop {name}" for name in container_names]
        elif operation == "start":
            commands = [f"docker start {name}" for name in container_names]
        elif operation == "restart":
            commands = [f"docker restart {name}" for name in container_names]
        else:
            self.logger.error("Unsupported batch operation: %s", operation)
            raise ValueError(f"Unsupported operation: {operation}")

        self.logger.debug("Executing %d commands concurrently", len(commands))
        results = await self.execute_multiple_commands(commands)

        responses = []
        for i, result in enumerate(results):
            if operation == "stop":
                responses.append(ContainerOperationResponse(
                    success=result.success,
                    container_name=container_names[i],
                    operation=operation,
                    previous_status=ContainerStatus.RUNNING,
                    current_status=ContainerStatus.STOPPED if result.success else None,
                    message=f"Container {container_names[i]} {operation}ed successfully" if result.success else f"Failed to {operation} container {container_names[i]}",
                    error=result.error
                ))
            elif operation == "start":
                responses.append(ContainerOperationResponse(
                    success=result.success,
                    container_name=container_names[i],
                    operation=operation,
                    previous_status=ContainerStatus.STOPPED,
                    current_status=ContainerStatus.RUNNING if result.success else None,
                    message=f"Container {container_names[i]} {operation}ed successfully" if result.success else f"Failed to {operation} container {container_names[i]}",
                    error=result.error
                ))
            elif operation == "restart":
                responses.append(ContainerOperationResponse(
                    success=result.success,
                    container_name=container_names[i],
                    operation=operation,
                    previous_status=ContainerStatus.RUNNING,
                    current_status=ContainerStatus.RUNNING if result.success else None,
                    message=f"Container {container_names[i]} {operation}ed successfully" if result.success else f"Failed to {operation} container {container_names[i]}",
                    error=result.error
                ))

        success_count = sum(1 for r in responses if r.success)
        failure_count = len(responses) - success_count
        self.logger.info("Batch %s operation completed: %d successful, %d failed", operation, success_count,
                         failure_count)

        return responses


__all__ = [
    "DockerService"
]
