"""
Tests for DockerService.
"""
import json
from .base_test import BaseDockerServiceTest
from backend.src.services.v1.docker_service import DockerService
from backend.src.schemas.v1.docker import (
    ContainerStatus, HealthStatus, RedeployRequest
)


class TestDockerService(BaseDockerServiceTest):
    """Test the DockerService class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = DockerService()

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service.system_gateway)

    def test_parse_status(self):
        """Test container status parsing."""
        # Test valid statuses
        self.assertEqual(
            self.service._parse_status("running"),
            ContainerStatus.RUNNING
        )
        self.assertEqual(
            self.service._parse_status("stopped"),
            ContainerStatus.STOPPED
        )
        self.assertEqual(
            self.service._parse_status("paused"),
            ContainerStatus.PAUSED
        )

        # Test case insensitive
        self.assertEqual(
            self.service._parse_status("RUNNING"),
            ContainerStatus.RUNNING
        )

        # Test unknown status
        self.assertIsNone(self.service._parse_status("unknown"))
        self.assertIsNone(self.service._parse_status(None))

    def test_parse_health_status(self):
        """Test health status parsing."""
        # Test valid health statuses
        self.assertEqual(
            self.service._parse_health_status("healthy"),
            HealthStatus.HEALTHY
        )
        self.assertEqual(
            self.service._parse_health_status("unhealthy"),
            HealthStatus.UNHEALTHY
        )
        self.assertEqual(
            self.service._parse_health_status("starting"),
            HealthStatus.STARTING
        )
        self.assertEqual(
            self.service._parse_health_status("none"),
            HealthStatus.NONE
        )

        # Test case insensitive
        self.assertEqual(
            self.service._parse_health_status("HEALTHY"),
            HealthStatus.HEALTHY
        )

        # Test unknown status
        self.assertEqual(
            self.service._parse_health_status("unknown"),
            HealthStatus.NONE
        )
        self.assertEqual(
            self.service._parse_health_status(None),
            HealthStatus.NONE
        )

    def test_parse_compose_labels_from_dict(self):
        """Test compose labels parsing from dictionary."""
        labels = {
            "com.docker.compose.project": "test_project",
            "com.docker.compose.service": "web",
            "com.docker.compose.config-hash": "abc123",
            "com.docker.compose.container-number": "1",
            "com.docker.compose.depends_on": "db",
            "com.docker.compose.version": "3.8",
            "com.docker.compose.project.config_files": "docker-compose.yml",
            "com.docker.compose.project.working_dir": "/app",
            "other.label": "value"
        }

        result = self.service._parse_compose_labels_from_dict(labels)

        self.assertEqual(result["project"], "test_project")
        self.assertEqual(result["service"], "web")
        self.assertEqual(result["config_hash"], "abc123")
        self.assertEqual(result["container_number"], "1")
        self.assertEqual(result["depends_on"], "db")
        self.assertEqual(result["version"], "3.8")
        self.assertEqual(result["config_files"], "docker-compose.yml")
        self.assertEqual(result["working_dir"], "/app")
        self.assertNotIn("other.label", result)

    def test_parse_compose_labels_from_string(self):
        """Test compose labels parsing from string."""
        labels_str = "com.docker.compose.project=test_project,com.docker.compose.service=web,other.label=value"

        result = self.service._parse_compose_labels(labels_str)

        self.assertEqual(result["project"], "test_project")
        self.assertEqual(result["service"], "web")
        self.assertNotIn("other.label", result)

    def test_parse_compose_labels_empty(self):
        """Test compose labels parsing with empty input."""
        self.assertEqual(self.service._parse_compose_labels(""), {})
        self.assertEqual(self.service._parse_compose_labels(None), {})

    def test_format_size(self):
        """Test size formatting."""
        self.assertEqual(self.service._format_size(1024), "1024.0 B")
        self.assertEqual(self.service._format_size(1024 * 1024), "1024.0 KB")
        self.assertEqual(self.service._format_size(
            1024 * 1024 * 1024), "1024.0 MB")
        self.assertEqual(self.service._format_size(
            1024 * 1024 * 1024 * 1024), "1024.0 GB")

    def test_build_deploy_command(self):
        """Test basic deploy command building."""
        command = self.service._build_deploy_command(
            "test_container", "nginx:latest")
        self.assertEqual(
            command, "docker run --name test_container nginx:latest")

        command = self.service._build_deploy_command("test_container", None)
        self.assertEqual(command, "docker run --name test_container")

    def test_build_deploy_command_from_inspect(self):
        """Test comprehensive deploy command building from inspect data."""
        container_data = {
            "Name": "/test_container",
            "Config": {
                "Image": "nginx:latest",
                "Env": ["ENV_VAR=value", "PATH=/usr/local/bin"],
                "WorkingDir": "/app",
                "User": "nginx"
            },
            "NetworkSettings": {
                "Ports": {
                    "80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]
                }
            },
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": "/host/path",
                    "Destination": "/container/path",
                    "RW": True
                }
            ],
            "HostConfig": {
                "RestartPolicy": {"Name": "unless-stopped"}
            }
        }

        command = self.service._build_deploy_command_from_inspect(
            container_data)

        self.assertIn("docker run -d", command)
        self.assertIn("--name test_container", command)
        self.assertIn("nginx:latest", command)
        self.assertIn("-p 8080:80", command)
        self.assertIn("-v /host/path:/container/path", command)
        self.assertIn("-e ENV_VAR=value", command)
        self.assertIn("-w /app", command)
        self.assertIn("-u nginx", command)
        self.assertIn("--restart unless-stopped", command)

    def test_build_redeploy_command(self):
        """Test redeploy command building."""
        request = RedeployRequest(
            container_name="test_container",
            image="nginx:latest",
            environment_vars={"ENV_VAR": "value"},
            ports={"8080": "80"},
            volumes=["/host:/container"]
        )

        command = self.service._build_redeploy_command(request, "nginx:latest")

        self.assertIn("docker run -d", command)
        self.assertIn("--name test_container", command)
        self.assertIn("nginx:latest", command)
        self.assertIn("-e ENV_VAR=value", command)
        self.assertIn("-p 8080:80", command)
        self.assertIn("-v /host:/container", command)

    async def test_get_container_info_success(self):
        """Test successful container info retrieval."""
        # Mock docker inspect output
        inspect_output = {
            "Id": "container123",
            "Name": "/test_container",
            "Config": {
                "Image": "nginx:latest",
                "Env": ["ENV_VAR=value"],
                "WorkingDir": "/app",
                "User": "nginx"
            },
            "Created": "2023-01-01T00:00:00Z",
            "State": {
                "Status": "running",
                "Health": {"Status": "healthy"}
            },
            "NetworkSettings": {
                "Ports": {
                    "80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]
                }
            },
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": "/host/path",
                    "Destination": "/container/path",
                    "RW": True
                }
            ],
            "HostConfig": {
                "RestartPolicy": {"Name": "unless-stopped"}
            }
        }

        self.mock_system_gateway.set_mock_response(
            "docker inspect test_container --format json",
            success=True,
            output=json.dumps(inspect_output)
        )

        result = await self.service.get_container_info("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(result.container_id, "container123")
        self.assertEqual(result.status, ContainerStatus.RUNNING)
        self.assertEqual(result.image, "nginx:latest")
        self.assertEqual(result.health_status, HealthStatus.HEALTHY)
        self.assertEqual(len(result.ports), 1)
        self.assertEqual(len(result.mounts), 1)

    async def test_get_container_info_failure(self):
        """Test container info retrieval failure."""
        self.mock_system_gateway.set_mock_response(
            "docker inspect test_container --format json",
            success=False,
            output="",
            error="Container not found"
        )

        result = await self.service.get_container_info("test_container")

        self.assertFalse(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertIn("Container not found", result.error)

    async def test_get_container_info_json_error(self):
        """Test container info retrieval with JSON parsing error."""
        self.mock_system_gateway.set_mock_response(
            "docker inspect test_container --format json",
            success=True,
            output="invalid json"
        )

        result = await self.service.get_container_info("test_container")

        self.assertFalse(result.success)
        self.assertIn("JSON decode error", result.error)

    async def test_list_containers_success(self):
        """Test successful container listing."""
        # Mock docker ps output
        ps_output = [
            {
                "ID": "container1",
                "Image": "nginx:latest",
                "Command": "nginx -g 'daemon off;'",
                "CreatedAt": "2023-01-01T00:00:00Z",
                "State": "running",
                "Status": "Up 2 hours",
                "Ports": "0.0.0.0:8080->80/tcp",
                "Names": "web_container",
                "Labels": "com.docker.compose.project=test,com.docker.compose.service=web",
                "LocalVolumes": "0",
                "Mounts": "/host:/container",
                "Networks": "bridge",
                "Platform": {"architecture": "amd64", "os": "linux"},
                "RunningFor": "2 hours",
                "Size": "100MB"
            }
        ]

        self.mock_system_gateway.set_mock_response(
            "docker ps --format json",
            success=True,
            output="\n".join(json.dumps(entry) for entry in ps_output)
        )

        result = await self.service.list_containers()

        self.assertTrue(result.success)
        self.assertEqual(len(result.containers), 1)
        self.assertEqual(result.total_count, 1)
        self.assertEqual(result.running_count, 1)
        self.assertEqual(result.stopped_count, 0)

    async def test_list_containers_all(self):
        """Test listing all containers including stopped ones."""
        self.mock_system_gateway.set_mock_response(
            "docker ps -a --format json",
            success=True,
            output="[]"
        )

        result = await self.service.list_containers(all_containers=True)

        self.assertTrue(result.success)
        self.assertEqual(len(result.containers), 0)

    async def test_stop_container_success(self):
        """Test successful container stop."""
        self.mock_system_gateway.set_mock_response(
            "docker stop test_container",
            success=True,
            output="test_container"
        )

        result = await self.service.stop_container("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(result.operation, "stop")
        self.assertEqual(result.previous_status, ContainerStatus.RUNNING)
        self.assertEqual(result.current_status, ContainerStatus.STOPPED)

    async def test_start_container_success(self):
        """Test successful container start."""
        self.mock_system_gateway.set_mock_response(
            "docker start test_container",
            success=True,
            output="test_container"
        )

        result = await self.service.start_container("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(result.operation, "start")
        self.assertEqual(result.previous_status, ContainerStatus.STOPPED)
        self.assertEqual(result.current_status, ContainerStatus.RUNNING)

    async def test_restart_container_success(self):
        """Test successful container restart."""
        self.mock_system_gateway.set_mock_response(
            "docker restart test_container",
            success=True,
            output="test_container"
        )

        result = await self.service.restart_container("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(result.operation, "restart")
        self.assertEqual(result.previous_status, ContainerStatus.RUNNING)
        self.assertEqual(result.current_status, ContainerStatus.RUNNING)

    async def test_health_check_container_success(self):
        """Test successful container health check."""
        self.mock_system_gateway.set_mock_response(
            "docker inspect --format='{{.State.Health.Status}}' test_container",
            success=True,
            output="healthy"
        )

        result = await self.service.health_check_container("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(result.health_status, HealthStatus.HEALTHY)

    async def test_health_check_container_no_health(self):
        """Test container health check with no health check configured."""
        self.mock_system_gateway.set_mock_response(
            "docker inspect --format='{{.State.Health.Status}}' test_container",
            success=True,
            output=""
        )

        result = await self.service.health_check_container("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.health_status, HealthStatus.NONE)

    async def test_get_container_logs_success(self):
        """Test successful container logs retrieval."""
        logs_output = "Line 1\nLine 2\nLine 3"
        self.mock_system_gateway.set_mock_response(
            "docker logs --tail 100 test_container",
            success=True,
            output=logs_output
        )

        result = await self.service.get_container_logs("test_container", 100)

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(len(result.logs), 3)
        self.assertEqual(result.total_lines, 3)
        self.assertEqual(result.tail_lines, 100)

    async def test_remove_container_success(self):
        """Test successful container removal."""
        self.mock_system_gateway.set_mock_response(
            "docker rm test_container",
            success=True,
            output="test_container"
        )

        result = await self.service.remove_container("test_container")

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertTrue(result.removed)
        self.assertFalse(result.force_used)

    async def test_remove_container_force(self):
        """Test container removal with force flag."""
        self.mock_system_gateway.set_mock_response(
            "docker rm -f test_container",
            success=True,
            output="test_container"
        )

        result = await self.service.remove_container("test_container", force=True)

        self.assertTrue(result.success)
        self.assertTrue(result.force_used)

    async def test_redeploy_container_success(self):
        """Test successful container redeployment."""
        # Mock get_container_info
        inspect_output = {
            "Id": "old_container_id",
            "Config": {"Image": "nginx:old"},
            "Name": "/test_container"
        }

        self.mock_system_gateway.set_mock_response(
            "docker inspect test_container --format json",
            success=True,
            output=json.dumps(inspect_output)
        )

        # Mock stop container
        self.mock_system_gateway.set_mock_response(
            "docker stop test_container",
            success=True,
            output="test_container"
        )

        # Mock remove container
        self.mock_system_gateway.set_mock_response(
            "docker rm -f test_container",
            success=True,
            output="test_container"
        )

        # Mock run new container
        self.mock_system_gateway.set_mock_response(
            "docker run -d --name test_container nginx:latest",
            success=True,
            output="new_container_id"
        )

        # Mock get new container ID
        self.mock_system_gateway.set_mock_response(
            "docker inspect --format='{{.Id}}' test_container",
            success=True,
            output="new_container_id"
        )

        request = RedeployRequest(
            container_name="test_container",
            image="nginx:latest"
        )

        result = await self.service.redeploy_container(request)

        self.assertTrue(result.success)
        self.assertEqual(result.container_name, "test_container")
        self.assertEqual(result.old_container_id, "old_container_id")
        self.assertEqual(result.new_container_id, "new_container_id")
        self.assertEqual(result.old_image, "nginx:old")
        self.assertEqual(result.new_image, "nginx:latest")

    async def test_execute_multiple_commands(self):
        """Test executing multiple commands."""
        commands = ["docker ps", "docker images", "docker version"]

        for cmd in commands:
            self.mock_system_gateway.set_mock_response(
                cmd,
                success=True,
                output=f"Output for {cmd}"
            )

        results = await self.service.execute_multiple_commands(commands)

        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertTrue(result.success)
            self.assertIn(commands[i], result.output)

    async def test_batch_container_operations(self):
        """Test batch container operations."""
        container_names = ["container1", "container2", "container3"]

        for name in container_names:
            self.mock_system_gateway.set_mock_response(
                f"docker stop {name}",
                success=True,
                output=name
            )

        results = await self.service.batch_container_operations(container_names, "stop")

        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertTrue(result.success)
            self.assertEqual(result.container_name, container_names[i])
            self.assertEqual(result.operation, "stop")

    def test_batch_container_operations_invalid_operation(self):
        """Test batch operations with invalid operation."""
        with self.assertRaises(ValueError):
            self.run_async(
                self.service.batch_container_operations(
                    ["container1"], "invalid")
            )
