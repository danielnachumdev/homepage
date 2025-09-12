"""
Tests for DockerComposeGateway using real Docker Compose projects.
"""

import asyncio
import tempfile
import os
from pathlib import Path
from tests.base import BaseTest
from backend.src.gateways.v1.docker_gateway.compose import DockerComposeGateway
from backend.src.gateways.v1.docker_gateway.models import ComposeProjectInfo, ComposeServiceInfo, DockerCommandResult


class TestDockerComposeGateway(BaseTest):
    """Test the DockerComposeGateway with real Docker Compose projects."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.test_project_name = f"test-gateway-{os.getpid()}"
        self.temp_dir = None
        self.compose_file = None

    def tearDown(self):
        """Clean up test compose projects."""
        super().tearDown()
        if self.compose_file and os.path.exists(self.compose_file):
            try:
                # Clean up compose project
                self.run_async(DockerComposeGateway.down(self.compose_file))
            except Exception:
                pass  # Project might not exist

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

    def test_01_compose_gateway_classmethods(self):
        """Test DockerComposeGateway classmethods."""
        self.logger.info("Testing DockerComposeGateway classmethods")

        # Test list compose projects
        projects = self.run_async(DockerComposeGateway.list())
        self.assertIsInstance(projects, list)
        self.logger.info(f"Found {len(projects)} compose projects")

    def test_02_compose_lifecycle_operations(self):
        """Test compose lifecycle operations."""
        self.logger.info("Testing compose lifecycle operations")

        # Create test compose file
        compose_file = self._create_test_compose_file()

        try:
            # Test up operation
            result = self.run_async(DockerComposeGateway.up(compose_file, detached=True))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "up")
            self.assertIn("compose_file", result.parsed_data)
            self.assertTrue(result.parsed_data["detached"])

            # Test ps operation (instance method)
            gateway = DockerComposeGateway(compose_file)
            services = self.run_async(gateway.ps())
            self.assertIsInstance(services, list)
            if services:
                service = services[0]
                self.assertIsInstance(service, ComposeServiceInfo)

            # Test logs operation
            logs_result = self.run_async(gateway.logs(tail_lines=10))
            self.assertIsInstance(logs_result, DockerCommandResult)
            self.assertEqual(logs_result.operation, "logs")

            # Test stop operation
            result = self.run_async(DockerComposeGateway.stop(compose_file))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "stop")

            # Test start operation
            result = self.run_async(DockerComposeGateway.start(compose_file))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "start")

            # Test restart operation
            result = self.run_async(DockerComposeGateway.restart(compose_file))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "restart")

        finally:
            # Clean up
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def test_03_compose_gateway_instance_methods(self):
        """Test DockerComposeGateway instance methods."""
        self.logger.info("Testing DockerComposeGateway instance methods")

        # Create test compose file
        compose_file = self._create_test_compose_file()

        try:
            # Start compose project
            self.run_async(DockerComposeGateway.up(compose_file, detached=True))

            # Create gateway instance
            gateway = DockerComposeGateway(compose_file)

            # Test exec
            exec_result = self.run_async(gateway.exec("test-service", "echo 'test command'"))
            self.assertIsInstance(exec_result, DockerCommandResult)
            self.assertEqual(exec_result.operation, "exec")
            self.assertIn("service", exec_result.parsed_data)
            self.assertEqual(exec_result.parsed_data["service"], "test-service")

            # Test logs with service
            logs_result = self.run_async(gateway.logs(service="test-service", tail_lines=5))
            self.assertIsInstance(logs_result, DockerCommandResult)
            self.assertEqual(logs_result.operation, "logs")
            self.assertIn("service", logs_result.parsed_data)

        finally:
            # Clean up
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def test_04_compose_command_result_properties(self):
        """Test DockerCommandResult properties for compose operations."""
        self.logger.info("Testing DockerCommandResult properties for compose")

        # Test with a simple command
        compose_file = self._create_test_compose_file()

        try:
            result = self.run_async(DockerComposeGateway.up(compose_file, detached=True))
            self.assertIsInstance(result, DockerCommandResult)

            # Test convenience properties
            self.assertIsNotNone(result.success)
            self.assertIsNotNone(result.stdout)
            self.assertIsNotNone(result.stderr)
            self.assertIsNotNone(result.return_code)
            self.assertIsNotNone(result.execution_time)

            # Test parsed data
            self.assertIsNotNone(result.parsed_data)
            self.assertIn("compose_file", result.parsed_data)
            self.assertIn("detached", result.parsed_data)

        finally:
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def test_05_compose_project_info_parsing(self):
        """Test compose project information parsing."""
        self.logger.info("Testing compose project information parsing")

        # Get compose projects list
        projects = self.run_async(DockerComposeGateway.list())

        if projects:
            project = projects[0]
            self.assertIsInstance(project, ComposeProjectInfo)

            # Test required fields
            self.assertIsNotNone(project.name)
            self.assertIsNotNone(project.status)
            self.assertIsInstance(project.config_files, list)
            self.assertIsInstance(project.services, list)

    def test_06_compose_service_info_parsing(self):
        """Test compose service information parsing."""
        self.logger.info("Testing compose service information parsing")

        # Create test compose file
        compose_file = self._create_test_compose_file()

        try:
            # Start compose project
            self.run_async(DockerComposeGateway.up(compose_file, detached=True))

            # Get services
            gateway = DockerComposeGateway(compose_file)
            services = self.run_async(gateway.ps())

            if services:
                service = services[0]
                self.assertIsInstance(service, ComposeServiceInfo)

                # Test required fields
                self.assertIsNotNone(service.name)
                self.assertIsNotNone(service.project)
                self.assertIsNotNone(service.status)
                self.assertIsInstance(service.ports, list)
                self.assertIsInstance(service.networks, list)

        finally:
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def test_07_compose_error_handling(self):
        """Test error handling for invalid compose operations."""
        self.logger.info("Testing compose error handling")

        # Test operations on non-existent compose file
        nonexistent_file = "/nonexistent/docker-compose.yml"

        result = self.run_async(DockerComposeGateway.up(nonexistent_file))
        self.assertIsInstance(result, DockerCommandResult)
        self.assertFalse(result.success)

        # Test operations on invalid compose file
        invalid_compose = self._create_invalid_compose_file()

        try:
            result = self.run_async(DockerComposeGateway.up(invalid_compose))
            self.assertIsInstance(result, DockerCommandResult)
            # May or may not succeed depending on Docker Compose validation
        finally:
            if os.path.exists(invalid_compose):
                os.remove(invalid_compose)

    def test_08_compose_concurrent_operations(self):
        """Test concurrent compose operations."""
        self.logger.info("Testing concurrent compose operations")

        # Create multiple test compose files
        compose_files = []
        for i in range(2):
            compose_file = self._create_test_compose_file()
            compose_files.append(compose_file)

        try:
            # Start projects concurrently
            up_tasks = [DockerComposeGateway.up(f, detached=True) for f in compose_files]
            results = self.run_async(asyncio.gather(*up_tasks))

            # Verify all operations completed
            self.assertEqual(len(results), 2)
            for result in results:
                self.assertIsInstance(result, DockerCommandResult)

        finally:
            # Clean up all projects
            for compose_file in compose_files:
                try:
                    self.run_async(DockerComposeGateway.down(compose_file))
                except Exception:
                    pass

    def test_09_compose_with_custom_project_dir(self):
        """Test compose operations with custom project directory."""
        self.logger.info("Testing compose with custom project directory")

        # Create test compose file
        compose_file = self._create_test_compose_file()
        project_dir = os.path.dirname(compose_file)

        try:
            # Test with custom project directory
            result = self.run_async(DockerComposeGateway.up(
                compose_file,
                project_dir=project_dir,
                detached=True
            ))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertIn("project_dir", result.parsed_data)
            self.assertEqual(result.parsed_data["project_dir"], project_dir)

        finally:
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def test_10_compose_pull_and_build_operations(self):
        """Test compose pull and build operations."""
        self.logger.info("Testing compose pull and build operations")

        # Create test compose file
        compose_file = self._create_test_compose_file()

        try:
            # Test pull operation
            result = self.run_async(DockerComposeGateway.pull(compose_file))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "pull")

            # Test build operation (may fail if no build context)
            result = self.run_async(DockerComposeGateway.build(compose_file))
            self.assertIsInstance(result, DockerCommandResult)
            self.assertEqual(result.operation, "build")

        finally:
            try:
                self.run_async(DockerComposeGateway.down(compose_file))
            except Exception:
                pass

    def _create_invalid_compose_file(self) -> str:
        """Create an invalid docker-compose.yml file for testing."""
        temp_dir = tempfile.mkdtemp()
        compose_file = os.path.join(temp_dir, "invalid-docker-compose.yml")

        invalid_content = """
version: '3.8'
services:
  invalid-service:
    image: nonexistent-image:latest
    invalid_key: invalid_value
    command: sleep 300
"""

        with open(compose_file, 'w') as f:
            f.write(invalid_content)

        return compose_file


__all__ = [
    "TestDockerComposeGateway"
]
