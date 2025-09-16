"""
Unit tests for NativeBackendDeployStep.
"""

import tempfile
import shutil
import os
import time
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.steps.native_backend_deploy_step import NativeBackendDeployStep


class TestNativeBackendDeployStep(BaseTest):
    """Test cases for NativeBackendDeployStep."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.backend_dir = self.project_root / "backend"
        self.backend_dir.mkdir(parents=True)
        
        # Create a simple backend that can run
        backend_main = '''
import sys
import time
import signal
import os

def signal_handler(sig, frame):
    print("Backend received signal, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print("Backend server started")
print("Backend PID:", os.getpid())

# Keep running until interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Backend shutting down...")
'''
        (self.backend_dir / "__main__.py").write_text(backend_main)
        
        # Create minimal requirements.txt
        (self.backend_dir / "requirements.txt").write_text("fastapi==0.104.1\nuvicorn==0.24.0")
        
        # Create __init__.py
        (self.backend_dir / "__init__.py").write_text("")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().tearDown()  # Call parent tearDown for asyncio cleanup

    def test_initialization(self):
        """Test step initialization."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            name="test-backend-deploy"
        )
        
        self.assertEqual(step.name, "test-backend-deploy")
        self.assertEqual(step.project_root, self.project_root)
        self.assertEqual(step.backend_dir, self.backend_dir)

    def test_initialization_with_defaults(self):
        """Test step initialization with default values."""
        step = NativeBackendDeployStep()
        
        # Should use current working directory as project root
        self.assertEqual(step.project_root, Path.cwd())
        self.assertEqual(step.backend_dir, Path.cwd() / "backend")

    def test_initialization_with_custom_backend_dir(self):
        """Test step initialization with custom backend directory."""
        custom_backend = self.project_root / "custom_backend"
        custom_backend.mkdir()
        (custom_backend / "__main__.py").write_text("print('test')")
        
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(custom_backend)
        )
        
        self.assertEqual(step.backend_dir, custom_backend)


    def test_validate_success(self):
        """Test validation with valid setup."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertTrue(result, "Validation should pass with valid setup")

    def test_validate_missing_backend_dir(self):
        """Test validation with missing backend directory."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir="/non/existent/path"
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing backend directory")

    def test_validate_missing_main_file(self):
        """Test validation with missing __main__.py."""
        # Remove __main__.py
        (self.backend_dir / "__main__.py").unlink()
        
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with missing __main__.py")

    def test_validate_syntax_error_in_main(self):
        """Test validation with syntax error in __main__.py."""
        # Create invalid Python file
        (self.backend_dir / "__main__.py").write_text("invalid python syntax !!!")
        
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.validate())
        self.assertFalse(result, "Validation should fail with syntax errors")

    def test_install_success(self):
        """Test successful installation (starting backend)."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertTrue(result, "Installation should succeed with valid setup")

    def test_install_missing_main_file(self):
        """Test installation with missing __main__.py."""
        (self.backend_dir / "__main__.py").unlink()
        
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.install())
        self.assertFalse(result, "Installation should fail with missing __main__.py")

    def test_install_already_running(self):
        """Test installation when backend is already running."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        # First install
        result1 = self.run_async(step.install())
        # Second install (should detect already running)
        result2 = self.run_async(step.install())
        result = result1 and result2
        self.assertTrue(result, "Installation should handle already running backend")

    def test_uninstall_success(self):
        """Test successful uninstallation (stopping backend)."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.uninstall())
        self.assertTrue(result, "Uninstall should succeed even if no processes are running")

    def test_uninstall_no_processes(self):
        """Test uninstall when no processes are running."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        result = self.run_async(step.uninstall())
        self.assertTrue(result, "Uninstall should succeed with no processes to stop")

    def test_is_process_running(self):
        """Test process running detection."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        # Initially no processes should be running
        result = self.run_async(step.is_process_running())
        self.assertFalse(result, "No processes should be running initially")

    def test_get_process_info(self):
        """Test process information collection."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        process_info = self.run_async(step.get_process_info())
        
        self.assertIn("status", process_info)
        self.assertIn("process_count", process_info)
        self.assertEqual(process_info["status"], "not_running")
        self.assertEqual(process_info["process_count"], 0)

    def test_get_metadata(self):
        """Test metadata collection."""
        step = NativeBackendDeployStep(
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
        step = NativeBackendDeployStep(
            project_root="/non/existent/path",
            backend_dir="/non/existent/backend"
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should still return metadata even with errors
        self.assertIn("name", metadata)
        self.assertIn("error", metadata)

    def test_step_string_representation(self):
        """Test string representation of the step."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            name="test-step"
        )
        
        str_repr = str(step)
        self.assertIn("NativeBackendDeployStep", str_repr)
        self.assertIn("test-step", str_repr)
        
        repr_str = repr(step)
        self.assertIn("NativeBackendDeployStep", repr_str)
        self.assertIn("test-step", repr_str)

    def test_step_initial_state(self):
        """Test initial state of the step."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        self.assertFalse(step.is_installed, "Step should not be installed initially")

    def test_main_file_detection(self):
        """Test that __main__.py is properly detected."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        # Test with existing __main__.py
        self.assertTrue((self.backend_dir / "__main__.py").exists())
        
        # Test with missing __main__.py
        (self.backend_dir / "__main__.py").unlink()
        self.assertFalse((self.backend_dir / "__main__.py").exists())

    def test_requirements_file_detection(self):
        """Test that requirements.txt is detected in metadata."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        async def run_metadata():
            return await step.get_metadata()
        
        metadata = self._run_async_test(run_metadata())
        
        # Should detect requirements file
        self.assertTrue((self.backend_dir / "requirements.txt").exists())

    def test_interpreter_detection(self):
        """Test Python interpreter detection."""
        step = NativeBackendDeployStep(
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir)
        )
        
        metadata = self.run_async(step.get_metadata())
        
        # Should have interpreter information
        self.assertIn("interpreter_path", metadata)
        self.assertIn("interpreter_working", metadata)
        self.assertIn("interpreter_version", metadata)


if __name__ == "__main__":
    unittest.main()
