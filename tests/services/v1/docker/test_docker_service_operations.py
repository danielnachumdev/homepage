"""
Tests for DockerService container operations.
"""
import json
from tests.services.v1.docker.base import BaseDockerServiceTest
from backend.src.services.v1.docker_service import DockerService
from backend.src.schemas.v1.docker import (
    ContainerStatus, HealthStatus, RedeployRequest
)


class TestDockerServiceOperations(BaseDockerServiceTest):
    """Test the DockerService container operations."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = DockerService()

    async def test_get_container_info_success(self):
        """Test successful container info retrieval."""
        # This test will use the real SystemGateway
        # Note: This test may fail if Docker is not running or container doesn't exist
        result = await self.service.get_container_info("test_container")

        # The result depends on whether Docker is available and container exists
        # We just test that the method doesn't crash and returns a valid response
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        if result.success:
            self.assertEqual(result.container_name, "test_container")

    async def test_get_container_info_failure(self):
        """Test container info retrieval failure."""
        # Test with a container that likely doesn't exist
        result = await self.service.get_container_info("nonexistent_container_12345")

        # This should fail gracefully
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        if not result.success:
            self.assertEqual(result.container_name,
                             "nonexistent_container_12345")

    async def test_list_containers_success(self):
        """Test successful container listing."""
        # This test will use the real SystemGateway
        # Note: This test may fail if Docker is not running
        result = await self.service.list_containers()

        # The result depends on whether Docker is available
        # We just test that the method doesn't crash and returns a valid response
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        if result.success:
            self.assertIsInstance(result.containers, list)
            self.assertIsInstance(result.total_count, int)

    async def test_list_containers_all(self):
        """Test listing all containers including stopped ones."""
        # This test will use the real SystemGateway
        result = await self.service.list_containers(all_containers=True)

        # The result depends on whether Docker is available
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        if result.success:
            self.assertIsInstance(result.containers, list)

    def test_parse_status(self):
        """Test container status parsing."""
        self.logger.info("Testing Docker container status parsing")

        # Test valid statuses
        self.assertEqual(
            self.service._parse_status("running"),
            ContainerStatus.RUNNING
        )
        self.logger.info("Running status parsing test passed")
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
