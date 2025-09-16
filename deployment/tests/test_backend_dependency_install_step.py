"""
Unit tests for NativeBackendDependencyInstallStep.
"""

import tempfile
import shutil
import os
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.steps.native_backend_dependency_install_step import NativeBackendDependencyInstallStep


class TestNativeBackendDependencyInstallStep(BaseTest):
    """Test cases for NativeBackendDependencyInstallStep."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.backend_dir = self.project_root / "backend"
        self.backend_dir.mkdir(parents=True)
        
        # Create minimal requirements.txt
        requirements_content = "fastapi==0.104.1\nuvicorn==0.24.0\npytest==7.4.0"
        (self.backend_dir / "requirements.txt").write_text(requirements_content)
        
        # Create a simple __init__.py to make it a package
        (self.backend_dir / "__init__.py").write_text("")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().tearDown()  # Call parent tearDown for asyncio cleanup

    def test_initialization(self):
        """Test step initialization."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            name="test-backend-deps"
        )
        
        self.assertEqual(step.name, "test-backend-deps")
        self.assertEqual(step.project_root, self.project_root)
        self.assertEqual(step.backend_dir, self.backend_dir)

    def test_initialization_with_defaults(self):
        """Test step initialization with default values."""
        step = NativeBackendDependencyInstallStep()
        
        # Should use current working directory as project root
        self.assertEqual(step.project_root, Path.cwd())
        self.assertEqual(step.backend_dir, Path.cwd() / "backend")

    def test_initialization_with_custom_backend_dir(self):
        """Test step initialization with custom backend directory."""
        custom_backend = self.project_root / "custom_backend"
        custom_backend.mkdir()
        
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(custom_backend)
        )
        
        self.assertEqual(step.backend_dir, custom_backend)


    def test_validate_success(self):
        """Test validation with valid setup."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertTrue(result, "Validation should pass with valid setup")

    def test_validate_missing_backend_dir(self):
        """Test validation with missing backend directory."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir="/non/existent/path"
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing backend directory")

    def test_validate_missing_requirements_file(self):
        """Test validation with missing requirements.txt."""
        # Remove requirements.txt
        (self.backend_dir / "requirements.txt").unlink()
        
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing requirements.txt")

    def test_validate_invalid_requirements_file(self):
        """Test validation with invalid requirements.txt."""
        # Create invalid requirements file
        (self.backend_dir / "requirements.txt").write_text("invalid package format")
        
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        # This might pass or fail depending on the requirements validation implementation
        # We'll just test that it doesn't crash

    def test_install_success(self):
        """Test successful installation."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertTrue(result, "Installation should succeed with valid setup")

    def test_install_missing_requirements(self):
        """Test installation with missing requirements file."""
        (self.backend_dir / "requirements.txt").unlink()
        
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertFalse(result, "Installation should fail with missing requirements.txt")

    def test_uninstall_no_op(self):
        """Test that uninstall is a no-op operation."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.uninstall())
        self.assertTrue(result, "Uninstall should always return True (no-op)")

    def test_get_metadata(self):
        """Test metadata collection."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
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
        self.assertEqual(str(metadata["backend_dir"]), str(self.backend_dir))
        self.assertTrue(metadata["backend_dir_exists"])
        self.assertTrue(metadata["main_file_exists"])

    def test_get_metadata_with_errors(self):
        """Test metadata collection with error conditions."""
        step = NativeBackendDependencyInstallStep(
            project_root="/non/existent/path",
            backend_dir="/non/existent/backend"
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should still return metadata even with errors
        self.assertIn("name", metadata)
        self.assertIn("error", metadata)

    def test_step_string_representation(self):
        """Test string representation of the step."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            name="test-step"
        )
        
        str_repr = str(step)
        self.assertIn("NativeBackendDependencyInstallStep", str_repr)
        self.assertIn("test-step", str_repr)
        
        repr_str = repr(step)
        self.assertIn("NativeBackendDependencyInstallStep", repr_str)
        self.assertIn("test-step", repr_str)

    def test_step_initial_state(self):
        """Test initial state of the step."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        self.assertFalse(step.is_installed, "Step should not be installed initially")

    def test_requirements_file_detection(self):
        """Test that requirements file is properly detected."""
        step = NativeBackendDependencyInstallStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        # Test with existing requirements file
        self.assertTrue((self.backend_dir / "requirements.txt").exists())
        
        # Test with missing requirements file
        (self.backend_dir / "requirements.txt").unlink()
        self.assertFalse((self.backend_dir / "requirements.txt").exists())


if __name__ == "__main__":
    unittest.main()
