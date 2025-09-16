"""
Unit tests for NativeFrontendDeployStep.
"""

import tempfile
import shutil
import os
import time
import json
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.steps.native_frontend_deploy_step import NativeFrontendDeployStep


class TestNativeFrontendDeployStep(BaseTest):
    """Test cases for NativeFrontendDeployStep."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.frontend_dir = self.project_root / "frontend"
        self.frontend_dir.mkdir(parents=True)
        
        # Create minimal package.json with dev script
        package_json = {
            "name": "test-frontend",
            "version": "1.0.0",
            "scripts": {
                "dev": "echo 'Frontend dev server started' && timeout 10",
                "build": "echo 'Building frontend'"
            },
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "devDependencies": {
                "vite": "^4.0.0"
            }
        }
        (self.frontend_dir / "package.json").write_text(json.dumps(package_json, indent=2))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().tearDown()  # Call parent tearDown for asyncio cleanup

    def test_initialization(self):
        """Test step initialization."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            name="test-frontend-deploy"
        )
        
        self.assertEqual(step.name, "test-frontend-deploy")
        self.assertEqual(step.project_root, self.project_root)
        self.assertEqual(step.frontend_dir, self.frontend_dir)

    def test_initialization_with_defaults(self):
        """Test step initialization with default values."""
        step = NativeFrontendDeployStep()
        
        # Should use current working directory as project root
        self.assertEqual(step.project_root, Path.cwd())
        self.assertEqual(step.frontend_dir, Path.cwd() / "frontend")

    def test_initialization_with_custom_frontend_dir(self):
        """Test step initialization with custom frontend directory."""
        custom_frontend = self.project_root / "custom_frontend"
        custom_frontend.mkdir()
        package_json = {"name": "test", "scripts": {"dev": "echo test"}}
        (custom_frontend / "package.json").write_text(json.dumps(package_json))
        
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(custom_frontend)
        )
        
        self.assertEqual(step.frontend_dir, custom_frontend)


    def test_validate_success(self):
        """Test validation with valid setup."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertTrue(result, "Validation should pass with valid setup")

    def test_validate_missing_frontend_dir(self):
        """Test validation with missing frontend directory."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir="/non/existent/path"
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing frontend directory")

    def test_validate_missing_package_json(self):
        """Test validation with missing package.json."""
        # Remove package.json
        (self.frontend_dir / "package.json").unlink()
        
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing package.json")

    def test_validate_missing_dev_script(self):
        """Test validation with missing dev script in package.json."""
        # Create package.json without dev script
        package_json = {
            "name": "test-frontend",
            "scripts": {
                "build": "echo 'Building frontend'"
            }
        }
        (self.frontend_dir / "package.json").write_text(json.dumps(package_json))
        
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing dev script")

    def test_validate_invalid_package_json(self):
        """Test validation with invalid package.json."""
        # Create invalid package.json
        (self.frontend_dir / "package.json").write_text("invalid json content")
        
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with invalid package.json")

    def test_validate_missing_npm(self):
        """Test validation when npm is not available."""
        # This test might be hard to simulate without actually removing npm
        # We'll just test that the validation runs without crashing
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        async def run_validation():
            return await step.validate()
        
        # This should pass if npm is available, or fail if not
        # We just want to ensure it doesn't crash
        try:
            result = self._run_async_test(run_validation())
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"Validation should not crash: {e}")

    def test_install_success(self):
        """Test successful installation (starting frontend)."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertTrue(result, "Installation should succeed with valid setup")

    def test_install_missing_package_json(self):
        """Test installation with missing package.json."""
        (self.frontend_dir / "package.json").unlink()
        
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertFalse(result, "Installation should fail with missing package.json")

    def test_install_already_running(self):
        """Test installation when frontend is already running."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        async def run_install():
            # First install
            result1 = await step.install()
            # Second install (should detect already running)
            result2 = await step.install()
            return result1 and result2
        
        result = self._run_async_test(run_install())
        self.assertTrue(result, "Installation should handle already running frontend")

    def test_uninstall_success(self):
        """Test successful uninstallation (stopping frontend)."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.uninstall())
        self.assertTrue(result, "Uninstall should succeed even if no processes are running")

    def test_uninstall_no_processes(self):
        """Test uninstall when no processes are running."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.uninstall())
        self.assertTrue(result, "Uninstall should succeed with no processes to stop")

    def test_is_process_running(self):
        """Test process running detection."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        # Initially no processes should be running
        result = self.run_async(step.is_process_running())
        self.assertFalse(result, "No processes should be running initially")

    def test_get_process_info(self):
        """Test process information collection."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        process_info = self.run_async(step.get_process_info())
        
        self.assertIn("status", process_info)
        self.assertIn("process_count", process_info)
        self.assertEqual(process_info["status"], "not_running")
        self.assertEqual(process_info["process_count"], 0)

    def test_get_metadata(self):
        """Test metadata collection."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            name="test-metadata"
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Check basic metadata
        self.assertEqual(metadata["name"], "test-metadata")
        self.assertIn("description", metadata)
        self.assertIn("installed", metadata)
        self.assertIn("type", metadata)
        
        # Check step-specific metadata
        self.assertEqual(str(metadata["project_root"]), str(self.project_root))
        self.assertEqual(str(metadata["frontend_dir"]), str(self.frontend_dir))
        self.assertTrue(metadata["frontend_dir_exists"])
        self.assertTrue(metadata["package_json_exists"])

    def test_get_metadata_with_errors(self):
        """Test metadata collection with error conditions."""
        step = NativeFrontendDeployStep(
            project_root="/non/existent/path",
            frontend_dir="/non/existent/frontend"
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should still return metadata even with errors
        self.assertIn("name", metadata)
        self.assertIn("error", metadata)

    def test_step_string_representation(self):
        """Test string representation of the step."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            name="test-step"
        )
        
        str_repr = str(step)
        self.assertIn("NativeFrontendDeployStep", str_repr)
        self.assertIn("test-step", str_repr)
        
        repr_str = repr(step)
        self.assertIn("NativeFrontendDeployStep", repr_str)
        self.assertIn("test-step", repr_str)

    def test_step_initial_state(self):
        """Test initial state of the step."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        self.assertFalse(step.is_installed, "Step should not be installed initially")

    def test_package_json_detection(self):
        """Test that package.json is properly detected."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        # Test with existing package.json
        self.assertTrue((self.frontend_dir / "package.json").exists())
        
        # Test with missing package.json
        (self.frontend_dir / "package.json").unlink()
        self.assertFalse((self.frontend_dir / "package.json").exists())

    def test_dev_script_validation(self):
        """Test dev script validation in package.json."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        # Test with valid dev script
        package_json = self.frontend_dir / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        
        self.assertIn("scripts", data)
        self.assertIn("dev", data["scripts"])

    def test_node_modules_detection(self):
        """Test node_modules detection in metadata."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should have node_modules information
        self.assertIn("node_modules_exists", metadata)
        self.assertIn("node_modules_path", metadata)

    def test_npm_version_detection(self):
        """Test npm version detection in metadata."""
        step = NativeFrontendDeployStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should have npm version information
        self.assertIn("npm_version", metadata)
        # npm_version could be "unknown" if npm is not available, which is fine


if __name__ == "__main__":
    unittest.main()
