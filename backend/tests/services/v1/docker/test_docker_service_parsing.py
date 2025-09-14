"""
Tests for DockerService parsing methods.
"""
import json
from backend.tests.services.v1.docker.base import BaseDockerServiceTest
from backend.src.services.v1.docker_service import DockerService
from backend.src.schemas.v1.docker import (
    ContainerStatus, HealthStatus, RedeployRequest
)


class TestDockerServiceParsing(BaseDockerServiceTest):
    """Test the DockerService parsing methods."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = DockerService()

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
        self.assertEqual(self.service._format_size(1024 * 1024 * 1024), "1024.0 MB")
        self.assertEqual(self.service._format_size(1024 * 1024 * 1024 * 1024), "1024.0 GB")

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

        command = self.service._build_deploy_command_from_inspect(container_data)

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
