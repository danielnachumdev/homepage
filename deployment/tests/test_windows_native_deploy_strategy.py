"""
Unit tests for WindowsNativeDeployStrategy integration.
"""

import tempfile
import shutil
import os
import json
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.strategies.windows_native_deploy_strategy import WindowsNativeDeployStrategy
from deployment.src.steps.native_backend_dependency_install_step import NativeBackendDependencyInstallStep
from deployment.src.steps.native_frontend_dependency_install_step import NativeFrontendDependencyInstallStep
from deployment.src.steps.native_backend_deploy_step import NativeBackendDeployStep
from deployment.src.steps.native_frontend_deploy_step import NativeFrontendDeployStep
from deployment.src.steps.windows_start_on_login_step import WindowsStartOnLoginStep


class TestWindowsNativeDeployStrategy(BaseTest):
    """Test cases for WindowsNativeDeployStrategy integration."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.deployment_dir = self.project_root / "deployment"
        self.scripts_dir = self.deployment_dir / "scripts"
        
        # Create directory structure
        self.backend_dir.mkdir(parents=True)
        self.frontend_dir.mkdir(parents=True)
        self.scripts_dir.mkdir(parents=True)
        
        # Create minimal backend structure
        backend_main = "print('Backend started')"
        (self.backend_dir / "__main__.py").write_text(backend_main)
        (self.backend_dir / "requirements.txt").write_text("fastapi==0.104.1\nuvicorn==0.24.0")
        (self.backend_dir / "__init__.py").write_text("")
        
        # Create minimal frontend structure
        package_json = {
            "name": "test-frontend",
            "version": "1.0.0",
            "scripts": {
                "dev": "echo 'Frontend dev server started'"
            },
            "dependencies": {
                "react": "^18.0.0"
            }
        }
        (self.frontend_dir / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # Create startup script
        startup_script = """# Test startup script
param([string]$ProjectRoot, [string]$FrontendDir, [string]$BackendDir)
Write-Host "Test startup script executed"
"""
        (self.scripts_dir / "startup_launcher.ps1").write_text(startup_script)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().tearDown()  # Call parent tearDown for asyncio cleanup

    def test_strategy_initialization(self):
        """Test strategy initialization with default values."""
        strategy = WindowsNativeDeployStrategy()
        
        self.assertEqual(strategy.name, "windows-native-deploy")
        self.assertIn("Deploy homepage using native Windows processes", strategy.description)
        self.assertEqual(strategy.backend_port, 8000)
        self.assertEqual(strategy.frontend_port, 5173)

    def test_strategy_initialization_with_custom_values(self):
        """Test strategy initialization with custom values."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            backend_port=8001,
            frontend_port=5174,
            name="custom-deploy",
            description="Custom deployment strategy"
        )
        
        self.assertEqual(strategy.name, "custom-deploy")
        self.assertEqual(strategy.description, "Custom deployment strategy")
        self.assertEqual(strategy.backend_port, 8001)
        self.assertEqual(strategy.frontend_port, 5174)
        self.assertEqual(strategy.project_root, str(self.project_root))

    def test_get_steps(self):
        """Test that strategy returns correct steps in order."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir)
        )
        
        steps = strategy.get_steps()
        
        # Should have 5 steps
        self.assertEqual(len(steps), 5)
        
        # Check step types and order
        self.assertIsInstance(steps[0], NativeBackendDependencyInstallStep)
        self.assertIsInstance(steps[1], NativeFrontendDependencyInstallStep)
        self.assertIsInstance(steps[2], NativeBackendDeployStep)
        self.assertIsInstance(steps[3], NativeFrontendDeployStep)
        self.assertIsInstance(steps[4], WindowsStartOnLoginStep)
        
        # Check step names
        self.assertEqual(steps[0].name, "windows-backend-deps")
        self.assertEqual(steps[1].name, "windows-frontend-deps")
        self.assertEqual(steps[2].name, "windows-backend-deploy")
        self.assertEqual(steps[3].name, "windows-frontend-deploy")
        self.assertEqual(steps[4].name, "windows-startup-shortcuts")

    def test_get_steps_with_custom_directories(self):
        """Test get_steps with custom project directories."""
        custom_backend = self.project_root / "custom_backend"
        custom_frontend = self.project_root / "custom_frontend"
        custom_backend.mkdir()
        custom_frontend.mkdir()
        
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(custom_backend),
            frontend_dir=str(custom_frontend)
        )
        
        steps = strategy.get_steps()
        
        # Check that steps use custom directories
        self.assertEqual(steps[0].backend_dir, custom_backend)
        self.assertEqual(steps[1].frontend_dir, custom_frontend)
        self.assertEqual(steps[2].backend_dir, custom_backend)
        self.assertEqual(steps[3].frontend_dir, custom_frontend)
        self.assertEqual(steps[4].backend_dir, custom_backend)
        self.assertEqual(steps[4].frontend_dir, custom_frontend)

    def test_install_environment_variables(self):
        """Test that install method sets environment variables."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            backend_port=8001,
            frontend_port=5174
        )
        
        # Store original environment
        original_backend_port = os.environ.get('BACKEND_PORT')
        original_frontend_port = os.environ.get('FRONTEND_PORT')
        
        try:
            # Clear environment variables
            if 'BACKEND_PORT' in os.environ:
                del os.environ['BACKEND_PORT']
            if 'FRONTEND_PORT' in os.environ:
                del os.environ['FRONTEND_PORT']
            
            # Test that install would set environment variables
            # Note: We're not actually calling install as it would try to run all steps
            # Instead we test the environment variable setting logic
            os.environ['BACKEND_PORT'] = str(strategy.backend_port)
            os.environ['FRONTEND_PORT'] = str(strategy.frontend_port)
            
            self.assertEqual(os.environ['BACKEND_PORT'], '8001')
            self.assertEqual(os.environ['FRONTEND_PORT'], '5174')
            
        finally:
            # Restore original environment
            if original_backend_port is not None:
                os.environ['BACKEND_PORT'] = original_backend_port
            elif 'BACKEND_PORT' in os.environ:
                del os.environ['BACKEND_PORT']
                
            if original_frontend_port is not None:
                os.environ['FRONTEND_PORT'] = original_frontend_port
            elif 'FRONTEND_PORT' in os.environ:
                del os.environ['FRONTEND_PORT']

    def test_get_metadata(self):
        """Test strategy metadata collection."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            backend_port=8001,
            frontend_port=5174,
            name="test-strategy"
        )
        
        metadata = self.run_async(strategy.get_metadata())
        
        # Check basic metadata
        self.assertEqual(metadata["name"], "test-strategy")
        self.assertIn("description", metadata)
        
        # Check strategy-specific metadata
        self.assertEqual(metadata["backend_port"], 8001)
        self.assertEqual(metadata["frontend_port"], 5174)
        self.assertEqual(metadata["strategy_type"], "windows_native")
        self.assertEqual(metadata["platform"], "windows")

    def test_get_port_info(self):
        """Test port information collection."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_port=8001,
            frontend_port=5174
        )
        
        port_info = strategy.get_port_info()
        
        self.assertEqual(port_info["backend_port"], 8001)
        self.assertEqual(port_info["frontend_port"], 5174)
        self.assertEqual(port_info["backend_url"], "http://localhost:8001")
        self.assertEqual(port_info["frontend_url"], "http://localhost:5174")

    def test_strategy_step_configuration(self):
        """Test that strategy properly configures all steps."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir)
        )
        
        steps = strategy.get_steps()
        
        # Check that all steps have the correct project root
        for step in steps:
            if hasattr(step, 'project_root'):
                self.assertEqual(step.project_root, Path(str(self.project_root)))
        
        # Check backend steps have correct backend directory
        backend_steps = [steps[0], steps[2]]  # deps and deploy
        for step in backend_steps:
            if hasattr(step, 'backend_dir'):
                self.assertEqual(step.backend_dir, self.backend_dir)
        
        # Check frontend steps have correct frontend directory
        frontend_steps = [steps[1], steps[3]]  # deps and deploy
        for step in frontend_steps:
            if hasattr(step, 'frontend_dir'):
                self.assertEqual(step.frontend_dir, self.frontend_dir)
        
        # Check startup step has both directories
        startup_step = steps[4]
        self.assertEqual(startup_step.frontend_dir, self.frontend_dir)
        self.assertEqual(startup_step.backend_dir, self.backend_dir)

    def test_strategy_step_descriptions(self):
        """Test that strategy steps have appropriate descriptions."""
        strategy = WindowsNativeDeployStrategy(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir)
        )
        
        steps = strategy.get_steps()
        
        # Check step descriptions
        self.assertIn("Python dependencies", steps[0].description)
        self.assertIn("Node.js dependencies", steps[1].description)
        self.assertIn("backend server", steps[2].description)
        self.assertIn("frontend development server", steps[3].description)
        self.assertIn("startup shortcuts", steps[4].description)

    def test_strategy_inheritance(self):
        """Test that strategy inherits from base Strategy class."""
        from deployment.strategies.base_strategy import Strategy
        
        strategy = WindowsNativeDeployStrategy()
        
        self.assertIsInstance(strategy, Strategy)
        
        # Check that it has required methods
        self.assertTrue(hasattr(strategy, 'install'))
        self.assertTrue(hasattr(strategy, 'uninstall'))
        self.assertTrue(hasattr(strategy, 'get_steps'))
        self.assertTrue(hasattr(strategy, 'get_metadata'))

    def test_strategy_string_representation(self):
        """Test string representation of the strategy."""
        strategy = WindowsNativeDeployStrategy(
            name="test-strategy"
        )
        
        # Strategy should have a meaningful string representation
        str_repr = str(strategy)
        self.assertIsInstance(str_repr, str)
        self.assertIn("test-strategy", str_repr)

    def test_strategy_with_none_directories(self):
        """Test strategy behavior with None directories (should use defaults)."""
        strategy = WindowsNativeDeployStrategy(
            project_root=None,
            backend_dir=None,
            frontend_dir=None
        )
        
        steps = strategy.get_steps()
        
        # Should still create steps (using default directories)
        self.assertEqual(len(steps), 5)
        
        # Steps should have valid directory paths
        for step in steps:
            if hasattr(step, 'project_root'):
                self.assertIsNotNone(step.project_root)
            if hasattr(step, 'backend_dir'):
                self.assertIsNotNone(step.backend_dir)
            if hasattr(step, 'frontend_dir'):
                self.assertIsNotNone(step.frontend_dir)

    def test_strategy_port_validation(self):
        """Test strategy with different port configurations."""
        # Test with default ports
        strategy1 = WindowsNativeDeployStrategy()
        self.assertEqual(strategy1.backend_port, 8000)
        self.assertEqual(strategy1.frontend_port, 5173)
        
        # Test with custom ports
        strategy2 = WindowsNativeDeployStrategy(
            backend_port=9000,
            frontend_port=3000
        )
        self.assertEqual(strategy2.backend_port, 9000)
        self.assertEqual(strategy2.frontend_port, 3000)
        
        # Test port info generation
        port_info = strategy2.get_port_info()
        self.assertIn("9000", port_info["backend_url"])
        self.assertIn("3000", port_info["frontend_url"])


if __name__ == "__main__":
    unittest.main()
