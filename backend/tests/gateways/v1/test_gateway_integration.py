"""
Integration tests for Docker gateways working together.
"""

import asyncio
import tempfile
import os
from pathlib import Path
from backend.tests.base import BaseTest
from backend.src.gateways.v1.docker_gateway.docker import DockerGateway
from backend.src.gateways.v1.docker_gateway.compose import DockerComposeGateway
from backend.src.gateways.v1.docker_gateway.models import ContainerInfo, ComposeProjectInfo, DockerCommandResult


class TestDockerGatewayIntegration(BaseTest):
    """Integration tests for Docker gateways working together."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.test_container_name = f"integration-test-{os.getpid()}"
        self.test_project_name = f"integration-test-{os.getpid()}"
        self.temp_dir = None
        self.compose_file = None

    def tearDown(self):
        """Clean up test resources."""
        super().tearDown()

        # Clean up container
        try:
            self.run_async(DockerGateway.delete(self.test_container_name, force=True))
        except Exception:
            pass

        # Clean up compose project
        if self.compose_file and os.path.exists(self.compose_file):
            try:
                self.run_async(DockerComposeGateway.down(self.compose_file))
            except Exception:
                pass

    def test_01_docker_and_compose_workflow(self):
        """Test complete workflow using both Docker and Compose gateways."""
        self.logger.info("Testing Docker and Compose workflow integration")

        # Step 1: Create a container using Docker gateway
        run_cmd = f"docker run -d --name {self.test_container_name} alpine:latest sleep 300"
        container_result = self.run_async(self._run_docker_command(run_cmd))

        if container_result.success:
            # Step 2: Verify container exists using Docker gateway
            containers = self.run_async(DockerGateway.list())
            container_found = any(c.names == self.test_container_name for c in containers)
            self.assertTrue(container_found, "Container should be found in list")

            # Step 3: Create a compose project
            compose_file = self._create_test_compose_file()

            try:
                # Step 4: Start compose project
                compose_result = self.run_async(DockerComposeGateway.up(compose_file, detached=True))
                self.assertIsInstance(compose_result, DockerCommandResult)

                # Step 5: Verify both container and compose project exist
                containers_after = self.run_async(DockerGateway.list())
                compose_projects = self.run_async(DockerComposeGateway.list())

                # Should have both our container and compose services
                container_still_exists = any(c.names == self.test_container_name for c in containers_after)
                self.assertTrue(container_still_exists, "Container should still exist")

                # Step 6: Test operations on both
                docker_gateway = DockerGateway(self.test_container_name)
                compose_gateway = DockerComposeGateway(compose_file)

                # Docker operations
                docker_logs = self.run_async(docker_gateway.logs(tail_lines=5))
                self.assertIsInstance(docker_logs, DockerCommandResult)

                # Compose operations
                compose_services = self.run_async(compose_gateway.ps())
                self.assertIsInstance(compose_services, list)

            finally:
                # Clean up compose project
                try:
                    self.run_async(DockerComposeGateway.down(compose_file))
                except Exception:
                    pass

    def test_02_concurrent_docker_and_compose_operations(self):
        """Test concurrent operations between Docker and Compose gateways."""
        self.logger.info("Testing concurrent Docker and Compose operations")

        # Create multiple containers and compose projects
        container_names = [f"{self.test_container_name}-{i}" for i in range(2)]
        compose_files = []

        try:
            # Create containers concurrently
            container_tasks = []
            for name in container_names:
                run_cmd = f"docker run -d --name {name} alpine:latest sleep 300"
                container_tasks.append(self._run_docker_command(run_cmd))

            container_results = self.run_async(asyncio.gather(*container_tasks))

            # Create compose projects concurrently
            compose_tasks = []
            for i in range(2):
                compose_file = self._create_test_compose_file()
                compose_files.append(compose_file)
                compose_tasks.append(DockerComposeGateway.up(compose_file, detached=True))

            compose_results = self.run_async(asyncio.gather(*compose_tasks))

            # Verify all operations completed
            self.assertEqual(len(container_results), 2)
            self.assertEqual(len(compose_results), 2)

            for result in container_results + compose_results:
                self.assertIsInstance(result, DockerCommandResult)

            # Test mixed operations
            mixed_tasks = [
                DockerGateway.list(),
                DockerComposeGateway.list(),
                DockerGateway.start(container_names[0]) if container_names else asyncio.sleep(0),
                DockerComposeGateway.ps(compose_files[0]) if compose_files else asyncio.sleep(0)
            ]

            mixed_results = self.run_async(asyncio.gather(*mixed_tasks, return_exceptions=True))

            # Verify mixed operations completed
            self.assertEqual(len(mixed_results), 4)

        finally:
            # Clean up all resources
            for name in container_names:
                try:
                    self.run_async(DockerGateway.delete(name, force=True))
                except Exception:
                    pass

            for compose_file in compose_files:
                try:
                    self.run_async(DockerComposeGateway.down(compose_file))
                except Exception:
                    pass

    def test_03_data_consistency_between_gateways(self):
        """Test data consistency between Docker and Compose gateways."""
        self.logger.info("Testing data consistency between gateways")

        # Create a compose project
        compose_file = self._create_test_compose_file()

        try:
            # Start compose project
            self.run_async(DockerComposeGateway.up(compose_file, detached=True))

            # Get data from both gateways
            containers = self.run_async(DockerGateway.list())
            compose_projects = self.run_async(DockerComposeGateway.list())
            compose_gateway = DockerComposeGateway(compose_file)
            compose_services = self.run_async(compose_gateway.ps())

            # Verify data consistency
            self.assertIsInstance(containers, list)
            self.assertIsInstance(compose_projects, list)
            self.assertIsInstance(compose_services, list)

            # Find our test project in compose projects
            test_project = next((p for p in compose_projects if self.test_project_name in p.name), None)
            if test_project:
                self.assertIsInstance(test_project, ComposeProjectInfo)
                self.assertIn(self.test_project_name, test_project.name)

            # Find our test services in containers
            test_containers = [c for c in containers if self.test_project_name in c.names]
            self.assertGreaterEqual(len(test_containers), 1)

        finally:
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def test_04_error_handling_across_gateways(self):
        """Test error handling consistency across both gateways."""
        self.logger.info("Testing error handling across gateways")

        # Test Docker gateway errors
        docker_result = self.run_async(DockerGateway.start("nonexistent_container"))
        self.assertIsInstance(docker_result, DockerCommandResult)
        self.assertFalse(docker_result.success)

        # Test Compose gateway errors
        compose_result = self.run_async(DockerComposeGateway.up("/nonexistent/compose.yml"))
        self.assertIsInstance(compose_result, DockerCommandResult)
        self.assertFalse(compose_result.success)

        # Test that both gateways return consistent error structures
        self.assertIsNotNone(docker_result.raw)
        self.assertIsNotNone(compose_result.raw)
        self.assertIsNotNone(docker_result.parsed_data)
        self.assertIsNotNone(compose_result.parsed_data)

    def test_05_performance_comparison(self):
        """Test performance comparison between Docker and Compose operations."""
        self.logger.info("Testing performance comparison")

        import time

        # Test Docker operations performance
        start_time = time.time()
        docker_containers = self.run_async(DockerGateway.list())
        docker_time = time.time() - start_time

        # Test Compose operations performance
        start_time = time.time()
        compose_projects = self.run_async(DockerComposeGateway.list())
        compose_time = time.time() - start_time

        self.logger.info(f"Docker list time: {docker_time:.3f}s")
        self.logger.info(f"Compose list time: {compose_time:.3f}s")

        # Both should be reasonably fast
        self.assertLess(docker_time, 5.0, "Docker operations should be fast")
        self.assertLess(compose_time, 5.0, "Compose operations should be fast")

    def test_06_resource_cleanup_integration(self):
        """Test proper resource cleanup across both gateways."""
        self.logger.info("Testing resource cleanup integration")

        # Create resources using both gateways
        container_name = f"{self.test_container_name}-cleanup"
        compose_file = self._create_test_compose_file()

        try:
            # Create container
            run_cmd = f"docker run -d --name {container_name} alpine:latest sleep 300"
            self.run_async(self._run_docker_command(run_cmd))

            # Create compose project
            self.run_async(DockerComposeGateway.up(compose_file, detached=True))

            # Verify resources exist
            containers = self.run_async(DockerGateway.list())
            container_exists = any(c.names == container_name for c in containers)
            self.assertTrue(container_exists, "Container should exist")

            compose_projects = self.run_async(DockerComposeGateway.list())
            project_exists = any(self.test_project_name in p.name for p in compose_projects)
            self.assertTrue(project_exists, "Compose project should exist")

        finally:
            # Clean up using both gateways
            try:
                self.run_async(DockerGateway.delete(container_name, force=True))
            except Exception:
                pass

            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

            # Verify cleanup
            containers_after = self.run_async(DockerGateway.list())
            container_still_exists = any(c.names == container_name for c in containers_after)
            self.assertFalse(container_still_exists, "Container should be cleaned up")

    def _create_test_compose_file(self) -> str:
        """Create a minimal test docker-compose.yml file."""
        self.temp_dir = tempfile.mkdtemp()
        self.compose_file = os.path.join(self.temp_dir, "docker-compose.yml")

        compose_content = f"""
version: '3.8'
services:
  test-service:
    image: alpine:latest
    container_name: {self.test_project_name}-test-service
    command: sleep 300
    labels:
      - com.docker.compose.project={self.test_project_name}
      - com.docker.compose.service=test-service
"""

        with open(self.compose_file, 'w') as f:
            f.write(compose_content)

        return self.compose_file

    async def _run_docker_command(self, command: str) -> DockerCommandResult:
        """Helper method to run a raw Docker command."""
        from backend.src.utils.command import AsyncCommand
        from backend.src.gateways.v1.docker_gateway.models import DockerCommandResult

        async_cmd = AsyncCommand.cmd(command)
        result = await async_cmd.execute()
        return DockerCommandResult(
            raw=result,
            operation="run",
            parsed_data={"command": command}
        )


__all__ = [
    "TestDockerGatewayIntegration"
]
