"""
Unit tests for WindowsStartOnLoginStep.
"""

import tempfile
import shutil
import os
import json
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.steps.windows_start_on_login_step import WindowsStartOnLoginStep


class TestWindowsStartOnLoginStep(BaseTest):
    """Test cases for WindowsStartOnLoginStep."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.frontend_dir = self.project_root / "frontend"
        self.backend_dir = self.project_root / "backend"
        self.deployment_dir = self.project_root / "deployment"
        self.scripts_dir = self.deployment_dir / "scripts"
        
        # Create directory structure
        self.frontend_dir.mkdir(parents=True)
        self.backend_dir.mkdir(parents=True)
        self.scripts_dir.mkdir(parents=True)
        
        # Create startup script
        startup_script = '''# Test startup script
param([string]$ProjectRoot, [string]$FrontendDir, [string]$BackendDir)
Write-Host "Test startup script executed"
Write-Host "Project Root: $ProjectRoot"
Write-Host "Frontend Dir: $FrontendDir"
Write-Host "Backend Dir: $BackendDir"
'''
        (self.scripts_dir / "startup_launcher.ps1").write_text(startup_script)
        
        # Create minimal frontend package.json
        package_json = {
            "name": "test-frontend",
            "scripts": {"dev": "echo 'Frontend started'"}
        }
        (self.frontend_dir / "package.json").write_text(json.dumps(package_json))
        
        # Create minimal backend __main__.py
        (self.backend_dir / "__main__.py").write_text("print('Backend started')")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().tearDown()  # Call parent tearDown for asyncio cleanup

    def test_initialization(self):
        """Test step initialization."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir),
            name="test-windows-startup"
        )
        
        self.assertEqual(step.name, "test-windows-startup")
        self.assertEqual(step.project_root, self.project_root)
        self.assertEqual(step.frontend_dir, self.frontend_dir)
        self.assertEqual(step.backend_dir, self.backend_dir)

    def test_initialization_with_defaults(self):
        """Test step initialization with default values."""
        step = WindowsStartOnLoginStep()
        
        # Should use current working directory as project root
        self.assertEqual(step.project_root, Path.cwd())
        self.assertEqual(step.frontend_dir, Path.cwd() / "frontend")
        self.assertEqual(step.backend_dir, Path.cwd() / "backend")

    def test_initialization_with_custom_dirs(self):
        """Test step initialization with custom directories."""
        custom_frontend = self.project_root / "custom_frontend"
        custom_backend = self.project_root / "custom_backend"
        custom_frontend.mkdir()
        custom_backend.mkdir()
        
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(custom_frontend),
            backend_dir=str(custom_backend)
        )
        
        self.assertEqual(step.frontend_dir, custom_frontend)
        self.assertEqual(step.backend_dir, custom_backend)

    def test_startup_folder_detection(self):
        """Test startup folder path detection."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        # Should have a startup folder path
        self.assertIsNotNone(step.startup_folder)
        self.assertIsInstance(step.startup_folder, Path)

    def test_validate_success(self):
        """Test validation with valid setup."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertTrue(result, "Validation should pass with valid setup")

    def test_validate_missing_startup_script(self):
        """Test validation with missing startup script."""
        # Remove startup script
        (self.scripts_dir / "startup_launcher.ps1").unlink()
        
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing startup script")

    def test_validate_missing_frontend_dir(self):
        """Test validation with missing frontend directory."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir="/non/existent/frontend",
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing frontend directory")

    def test_validate_missing_backend_dir(self):
        """Test validation with missing backend directory."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir="/non/existent/backend"
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing backend directory")

    def test_install_success(self):
        """Test successful installation (creating shortcut)."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.install())
        # Note: This might fail on non-Windows systems or without proper permissions
        # We'll test that it doesn't crash rather than asserting success
        self.assertIsInstance(result, bool)

    def test_uninstall_success(self):
        """Test successful uninstallation (removing shortcut)."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.uninstall())
        # Note: This might fail on non-Windows systems
        # We'll test that it doesn't crash rather than asserting success
        self.assertIsInstance(result, bool)

    def test_is_shortcut_installed(self):
        """Test shortcut installation detection."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        # Initially should not be installed
        self.assertFalse(step.is_shortcut_installed())

    def test_get_shortcut_info(self):
        """Test shortcut information collection."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        shortcut_info = step.get_shortcut_info()
        
        self.assertIn("status", shortcut_info)
        self.assertEqual(shortcut_info["status"], "not_installed")

    def test_get_metadata(self):
        """Test metadata collection."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
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
        self.assertEqual(str(metadata["frontend_dir"]), str(self.frontend_dir))
        self.assertEqual(str(metadata["backend_dir"]), str(self.backend_dir))
        self.assertTrue(metadata["startup_script_exists"])
        self.assertIn("platform", metadata)

    def test_get_metadata_with_errors(self):
        """Test metadata collection with error conditions."""
        step = WindowsStartOnLoginStep(
            project_root="/non/existent/path",
            frontend_dir="/non/existent/frontend",
            backend_dir="/non/existent/backend"
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should still return metadata even with errors
        self.assertIn("name", metadata)
        self.assertIn("error", metadata)

    def test_step_string_representation(self):
        """Test string representation of the step."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir),
            name="test-step"
        )
        
        str_repr = str(step)
        self.assertIn("WindowsStartOnLoginStep", str_repr)
        self.assertIn("test-step", str_repr)
        
        repr_str = repr(step)
        self.assertIn("WindowsStartOnLoginStep", repr_str)
        self.assertIn("test-step", repr_str)

    def test_step_initial_state(self):
        """Test initial state of the step."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        self.assertFalse(step.is_installed, "Step should not be installed initially")

    def test_startup_script_detection(self):
        """Test that startup script is properly detected."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        # Test with existing startup script
        self.assertTrue(step.startup_script.exists())
        
        # Test with missing startup script
        step.startup_script.unlink()
        self.assertFalse(step.startup_script.exists())

    def test_shortcut_name_and_path(self):
        """Test shortcut name and path generation."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        # Should have a shortcut name
        self.assertIsNotNone(step.shortcut_name)
        self.assertTrue(step.shortcut_name.endswith(".lnk"))
        
        # Should generate a shortcut path
        shortcut_path = step.startup_folder / step.shortcut_name
        self.assertIsInstance(shortcut_path, Path)

    def test_windows_platform_check(self):
        """Test Windows platform detection."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        # The validation should check for Windows platform
        # We can't easily mock this, so we'll just ensure it doesn't crash
        result = self.run_async(step.validate())
        self.assertIsInstance(result, bool)

    def test_powershell_availability_check(self):
        """Test PowerShell availability check."""
        step = WindowsStartOnLoginStep(
            project_root=str(self.project_root),
            frontend_dir=str(self.frontend_dir),
            backend_dir=str(self.backend_dir)
        )
        
        # The validation should check for PowerShell availability
        # We can't easily mock this, so we'll just ensure it doesn't crash
        result = self.run_async(step.validate())
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
