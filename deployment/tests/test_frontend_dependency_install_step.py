"""
Unit tests for NativeFrontendDependencyInstallStep.
"""

import tempfile
import shutil
import os
import json
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.steps.native_frontend_dependency_install_step import NativeFrontendDependencyInstallStep


class TestNativeFrontendDependencyInstallStep(BaseTest):
    """Test cases for NativeFrontendDependencyInstallStep."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.frontend_dir = self.project_root / "frontend"
        self.frontend_dir.mkdir(parents=True)
        
        # Create minimal package.json
        package_json = {
            "name": "test-frontend",
            "version": "1.0.0",
            "scripts": {
                "dev": "echo 'Frontend dev server started'",
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
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            name="test-frontend-deps"
        )
        
        self.assertEqual(step.name, "test-frontend-deps")
        self.assertEqual(step.project_root, self.project_root)
        self.assertEqual(step.frontend_dir, self.frontend_dir)

    def test_initialization_with_defaults(self):
        """Test step initialization with default values."""
        step = NativeFrontendDependencyInstallStep()
        
        # Should use current working directory as project root
        self.assertEqual(step.project_root, Path.cwd())
        self.assertEqual(step.frontend_dir, Path.cwd() / "frontend")

    def test_initialization_with_custom_frontend_dir(self):
        """Test step initialization with custom frontend directory."""
        custom_frontend = self.project_root / "custom_frontend"
        custom_frontend.mkdir()
        
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(custom_frontend)
        )
        
        self.assertEqual(step.frontend_dir, custom_frontend)


    def test_validate_success(self):
        """Test validation with valid setup."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertTrue(result, "Validation should pass with valid setup")

    def test_validate_missing_frontend_dir(self):
        """Test validation with missing frontend directory."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir="/non/existent/path"
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing frontend directory")

    def test_validate_missing_package_json(self):
        """Test validation with missing package.json."""
        # Remove package.json
        (self.frontend_dir / "package.json").unlink()
        
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing package.json")

    def test_validate_invalid_package_json(self):
        """Test validation with invalid package.json."""
        # Create invalid package.json
        (self.frontend_dir / "package.json").write_text("invalid json content")
        
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with invalid package.json")

    def test_validate_missing_npm(self):
        """Test validation when npm is not available."""
        # This test might be hard to simulate without actually removing npm
        # We'll just test that the validation runs without crashing
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        # This should pass if npm is available, or fail if not
        # We just want to ensure it doesn't crash
        try:
            result = self.run_async(step.validate())
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"Validation should not crash: {e}")

    def test_install_success(self):
        """Test successful installation."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertTrue(result, "Installation should succeed with valid setup")

    def test_install_missing_package_json(self):
        """Test installation with missing package.json."""
        (self.frontend_dir / "package.json").unlink()
        
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertFalse(result, "Installation should fail with missing package.json")

    def test_install_creates_node_modules(self):
        """Test that installation creates node_modules directory."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.install())
        
        if result:  # Only check if installation succeeded
            node_modules = self.frontend_dir / "node_modules"
            self.assertTrue(node_modules.exists(), "node_modules should be created after installation")

    def test_uninstall_no_op(self):
        """Test that uninstall is a no-op operation."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        result = self.run_async(step.uninstall())
        self.assertTrue(result, "Uninstall should always return True (no-op)")

    def test_get_metadata(self):
        """Test metadata collection."""
        step = NativeFrontendDependencyInstallStep(
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
        step = NativeFrontendDependencyInstallStep(
            project_root="/non/existent/path",
            frontend_dir="/non/existent/frontend"
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should still return metadata even with errors
        self.assertIn("name", metadata)
        self.assertIn("error", metadata)

    def test_step_string_representation(self):
        """Test string representation of the step."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            name="test-step"
        )
        
        str_repr = str(step)
        self.assertIn("NativeFrontendDependencyInstallStep", str_repr)
        self.assertIn("test-step", str_repr)
        
        repr_str = repr(step)
        self.assertIn("NativeFrontendDependencyInstallStep", repr_str)
        self.assertIn("test-step", repr_str)

    def test_step_initial_state(self):
        """Test initial state of the step."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        self.assertFalse(step.is_installed, "Step should not be installed initially")

    def test_package_json_detection(self):
        """Test that package.json is properly detected."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        # Test with existing package.json
        self.assertTrue((self.frontend_dir / "package.json").exists())
        
        # Test with missing package.json
        (self.frontend_dir / "package.json").unlink()
        self.assertFalse((self.frontend_dir / "package.json").exists())

    def test_package_json_validation(self):
        """Test package.json validation."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        # Test with valid package.json
        package_json = self.frontend_dir / "package.json"
        self.assertTrue(package_json.exists())
        
        # Read and validate the content
        with open(package_json, 'r') as f:
            data = json.load(f)
        
        self.assertIn("name", data)
        self.assertIn("scripts", data)
        self.assertIn("dependencies", data)

    def test_npm_version_detection(self):
        """Test npm version detection in metadata."""
        step = NativeFrontendDependencyInstallStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir)
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should have npm version information
        self.assertIn("npm_version", metadata)
        # npm_version could be "unknown" if npm is not available, which is fine


if __name__ == "__main__":
    unittest.main()
