"""
Tests for DockerGateway using real Docker containers.
"""

import asyncio
import os
from backend.tests.base import BaseTest
from backend.src.gateways.v1.docker_gateway.docker import DockerGateway
from backend.src.gateways.v1.docker_gateway.models import ContainerInfo, DockerCommandResult, ContainerInspectInfo


class TestDockerGateway(BaseTest):
    """Test the DockerGateway with real Docker containers."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.test_container_name = f"test-gateway-{os.getpid()}"
        self.test_image = "alpine:latest"  # Small, fast image

    def tearDown(self):
        """Clean up test containers."""
        # Clean up test container if it exists
        try:
            self.run_async(DockerGateway.delete(self.test_container_name, force=True))
        except (RuntimeError, OSError, ValueError):
            pass  # Container might not exist
        super().tearDown()

    def test_01_docker_gateway_classmethods(self):
        """Test DockerGateway classmethods."""
        self.logger.info("Testing DockerGateway classmethods")

        # Test list containers
        containers = self.run_async(DockerGateway.list())
        self.assertIsInstance(containers, list)
        self.logger.info("Found %d containers", len(containers))

        # Test list all containers
        all_containers = self.run_async(DockerGateway.list(all_containers=True))
        self.assertIsInstance(all_containers, list)
        self.assertGreaterEqual(len(all_containers), len(containers))

    def test_02_container_lifecycle_operations(self):
        """Test container lifecycle operations."""
        self.logger.info("Testing container lifecycle operations")

        # Create a test container
        run_cmd = f"docker run -d --name {self.test_container_name} {self.test_image} sleep 300"
        self.run_async(self._run_docker_command(run_cmd))

        try:
            # Test start operation
            result = self.run_async(DockerGateway.start(self.test_container_name))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "start")
            self.assertEqual(result.container_name, self.test_container_name)
            self.assertIsNotNone(result.raw)

            # Test stop operation
            result = self.run_async(DockerGateway.stop(self.test_container_name))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "stop")
            self.assertEqual(result.container_name, self.test_container_name)

            # Test restart operation
            result = self.run_async(DockerGateway.restart(self.test_container_name))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "restart")
            self.assertEqual(result.container_name, self.test_container_name)

        finally:
            # Clean up
            self.run_async(DockerGateway.delete(self.test_container_name, force=True))

    def test_03_docker_gateway_instance_methods(self):
        """Test DockerGateway instance methods."""
        self.logger.info("Testing DockerGateway instance methods")

        # Create a test container
        run_cmd = f"docker run -d --name {self.test_container_name} {self.test_image} sleep 300"
        self.run_async(self._run_docker_command(run_cmd))

        try:
            # Create gateway instance
            gateway = DockerGateway(self.test_container_name)

            # Test inspect
            inspect_result = self.run_async(gateway.inspect())
            if inspect_result:
                self.assertIsInstance(inspect_result, ContainerInspectInfo)
                self.assertEqual(inspect_result.name, self.test_container_name)
                self.assertEqual(inspect_result.image, self.test_image)

            # Test logs
            logs_result = self.run_async(gateway.logs(tail_lines=10))
            self.assertIsInstance(logs_result, DockerCommandResult)
            self.assertEqual(logs_result.operation, "logs")
            self.assertEqual(logs_result.container_name, self.test_container_name)
            self.assertIn("tail_lines", logs_result.parsed_data)

            # Test exec
            exec_result = self.run_async(gateway.exec("echo 'test command'"))
            self.assertIsInstance(exec_result, DockerCommandResult)
            self.assertEqual(exec_result.operation, "run")
            self.assertEqual(exec_result.container_name, self.test_container_name)
            self.assertIn("executed_command", exec_result.parsed_data)

        finally:
            # Clean up
            self.run_async(DockerGateway.delete(self.test_container_name, force=True))

    def test_04_docker_command_result_properties(self):
        """Test DockerCommandResult convenience properties."""
        self.logger.info("Testing DockerCommandResult properties")

        # Test with a simple command
        result = self.run_async(DockerGateway.start("nonexistent_container"))
        self.assertIsInstance(result, DockerCommandResult)

        # Test convenience properties
        self.assertIsNotNone(result.success)
        self.assertIsNotNone(result.stdout)
        self.assertIsNotNone(result.stderr)
        self.assertIsNotNone(result.return_code)
        self.assertIsNotNone(result.execution_time)

        # Test raw access
        self.assertIsNotNone(result.raw)
        self.assertEqual(result.success, result.raw.success)
        self.assertEqual(result.stdout, result.raw.stdout)

    def test_05_container_info_parsing(self):
        """Test container information parsing."""
        self.logger.info("Testing container information parsing")

        # Get container list
        containers = self.run_async(DockerGateway.list())

        if containers:
            container = containers[0]
            self.assertIsInstance(container, ContainerInfo)

            # Test required fields
            self.assertIsNotNone(container.id)
            self.assertIsNotNone(container.image)
            self.assertIsNotNone(container.status)
            self.assertIsNotNone(container.names)

            # Test platform info
            self.assertIsInstance(container.platform, dict)
            self.assertIn('architecture', container.platform)
            self.assertIn('os', container.platform)

    def test_06_error_handling(self):
        """Test error handling for invalid operations."""
        self.logger.info("Testing error handling")

        # Test operations on non-existent container
        result = self.run_async(DockerGateway.start("nonexistent_container_12345"))
        self.assertIsInstance(result, DockerCommandResult)
        self.assertFalse(result.success)
        self.assertNotEqual(result.return_code, 0)

        # Test delete non-existent container
        result = self.run_async(DockerGateway.delete("nonexistent_container_12345"))
        self.assertIsInstance(result, DockerCommandResult)
        self.assertFalse(result.success)

    def test_07_concurrent_operations(self):
        """Test concurrent Docker operations."""
        self.logger.info("Testing concurrent operations")

        # Create multiple test containers
        container_names = [f"{self.test_container_name}-{i}" for i in range(3)]

        try:
            # Create containers concurrently
            create_tasks = []
            for name in container_names:
                run_cmd = f"docker run -d --name {name} {self.test_image} sleep 300"
                create_tasks.append(self._run_docker_command(run_cmd))

            self.run_async(asyncio.gather(*create_tasks))

            # Test concurrent operations
            start_tasks = [DockerGateway.start(name) for name in container_names]
            results = self.run_async(asyncio.gather(*start_tasks))

            # Verify all operations completed
            self.assertEqual(len(results), 3)
            for result in results:
                self.assertIsInstance(result, DockerCommandResult)

        finally:
            # Clean up all containers
            for name in container_names:
                try:
                    self.run_async(DockerGateway.delete(name, force=True))
                except (RuntimeError, OSError, ValueError):
                    pass

    async def _run_docker_command(self, command: str) -> DockerCommandResult:
        """Helper method to run a raw Docker command."""
        from backend.src.utils.command import AsyncCommand
        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()
        return DockerCommandResult(
            raw=result,
            operation="run",
            parsed_data={"command": command}
        )


__all__ = [
    "TestDockerGateway"
]
