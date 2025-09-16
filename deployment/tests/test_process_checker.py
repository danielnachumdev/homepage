"""
Unit tests for process checker utilities.
"""

import tempfile
import shutil
from pathlib import Path
from deployment.tests.base import BaseTest
from deployment.src.utils.process_checker import (
    is_backend_running, is_frontend_running, kill_process, 
    kill_processes_carefully, ProcessSearchResult
)


class TestProcessChecker(BaseTest):
    """Test cases for process checker utilities."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call parent setUp for asyncio setup
        self.temp_dir = tempfile.mkdtemp(prefix="homepage_test_")
        self.project_root = Path(self.temp_dir)
        self.frontend_dir = self.project_root / "frontend"
        self.backend_dir = self.project_root / "backend"
        
        # Create directory structure
        self.frontend_dir.mkdir(parents=True)
        self.backend_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().tearDown()  # Call parent tearDown for asyncio cleanup

    def test_process_search_result_initialization(self):
        """Test ProcessSearchResult dataclass initialization."""
        result = ProcessSearchResult(
            found=True,
            processes=[{"pid": 1234, "name": "test"}],
            total_count=1
        )
        
        self.assertTrue(result.found)
        self.assertEqual(len(result.processes), 1)
        self.assertEqual(result.total_count, 1)
        self.assertEqual(result.processes[0]["pid"], 1234)

    def test_process_search_result_empty(self):
        """Test ProcessSearchResult with no processes."""
        result = ProcessSearchResult(
            found=False,
            processes=[],
            total_count=0
        )
        
        self.assertFalse(result.found)
        self.assertEqual(len(result.processes), 0)
        self.assertEqual(result.total_count, 0)

    def test_is_backend_running_no_processes(self):
        """Test backend process detection when no processes are running."""
        result = self.run_async(is_backend_running(
            str(self.project_root),
            str(self.backend_dir)
        ))
        
        self.assertIsInstance(result, ProcessSearchResult)
        self.assertFalse(result.found)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.processes), 0)

    def test_is_backend_running_with_defaults(self):
        """Test backend process detection with default backend directory."""
        result = self.run_async(is_backend_running(str(self.project_root)))
        
        self.assertIsInstance(result, ProcessSearchResult)
        self.assertFalse(result.found)
        self.assertEqual(result.total_count, 0)

    def test_is_frontend_running_no_processes(self):
        """Test frontend process detection when no processes are running."""
        result = self.run_async(is_frontend_running(
            str(self.project_root),
            str(self.frontend_dir)
        ))
        
        self.assertIsInstance(result, ProcessSearchResult)
        self.assertFalse(result.found)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.processes), 0)

    def test_is_frontend_running_with_defaults(self):
        """Test frontend process detection with default frontend directory."""
        result = self.run_async(is_frontend_running(str(self.project_root)))
        
        self.assertIsInstance(result, ProcessSearchResult)
        self.assertFalse(result.found)
        self.assertEqual(result.total_count, 0)

    def test_kill_process_invalid_pid(self):
        """Test killing a process with invalid PID."""
        # Use a PID that's unlikely to exist
        invalid_pid = 999999
        
        result = self.run_async(kill_process(invalid_pid))
        
        # Should return False for invalid PID
        self.assertFalse(result)

    def test_kill_process_with_timeout(self):
        """Test killing a process with custom timeout."""
        # Use a PID that's unlikely to exist
        invalid_pid = 999999
        
        result = self.run_async(kill_process(invalid_pid, timeout=5))
        
        # Should return False for invalid PID
        self.assertFalse(result)

    def test_kill_processes_carefully_empty_list(self):
        """Test killing processes with empty process list."""
        from unittest.mock import Mock
        
        logger = Mock()
        result = self.run_async(kill_processes_carefully(
            processes=[],
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            logger=logger
        ))
        
        # Should return True for empty list
        self.assertTrue(result)

    def test_kill_processes_carefully_invalid_processes(self):
        """Test killing processes with invalid process data."""
        from unittest.mock import Mock
        
        logger = Mock()
        
        # Test with invalid process data
        invalid_processes = [
            {"invalid": "data"},
            {"pid": "not_a_number", "cmdline": "test", "cwd": "test"}
        ]
        
        result = self.run_async(kill_processes_carefully(
            processes=invalid_processes,
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            logger=logger
        ))
        
        # Should handle invalid data gracefully
        self.assertIsInstance(result, bool)

    def test_kill_processes_carefully_backend_process(self):
        """Test killing backend processes."""
        from unittest.mock import Mock
        
        logger = Mock()
        
        # Create mock backend process
        backend_processes = [
            {
                "pid": 12345,
                "cmdline": "python __main__.py",
                "cwd": str(self.backend_dir),
                "name": "python"
            }
        ]
        
        result = self.run_async(kill_processes_carefully(
            processes=backend_processes,
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            logger=logger
        ))
        
        # Should attempt to kill the process (will fail since PID doesn't exist)
        self.assertIsInstance(result, bool)
        
        # Check that logger was called
        self.assertTrue(logger.info.called or logger.warning.called or logger.error.called)

    def test_kill_processes_carefully_frontend_process(self):
        """Test killing frontend processes."""
        from unittest.mock import Mock
        
        logger = Mock()
        
        # Create mock frontend process
        frontend_processes = [
            {
                "pid": 12346,
                "cmdline": "npm run dev",
                "cwd": str(self.frontend_dir),
                "name": "npm"
            }
        ]
        
        result = self.run_async(kill_processes_carefully(
            processes=frontend_processes,
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            logger=logger
        ))
        
        # Should attempt to kill the process (will fail since PID doesn't exist)
        self.assertIsInstance(result, bool)
        
        # Check that logger was called
        self.assertTrue(logger.info.called or logger.warning.called or logger.error.called)

    def test_kill_processes_carefully_cmd_process(self):
        """Test killing cmd.exe frontend processes."""
        from unittest.mock import Mock
        
        logger = Mock()
        
        # Create mock cmd.exe process running dev server
        cmd_processes = [
            {
                "pid": 12347,
                "cmdline": "cmd.exe /d /s /c vite --port 5173",
                "cwd": str(self.frontend_dir),
                "name": "cmd"
            }
        ]
        
        result = self.run_async(kill_processes_carefully(
            processes=cmd_processes,
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            logger=logger
        ))
        
        # Should attempt to kill the process (will fail since PID doesn't exist)
        self.assertIsInstance(result, bool)
        
        # Check that logger was called
        self.assertTrue(logger.info.called or logger.warning.called or logger.error.called)

    def test_kill_processes_carefully_unidentified_process(self):
        """Test handling of unidentified processes."""
        from unittest.mock import Mock
        
        logger = Mock()
        
        # Create mock process that doesn't match our patterns
        unidentified_processes = [
            {
                "pid": 12348,
                "cmdline": "notepad.exe",
                "cwd": "C:\\Windows\\System32",
                "name": "notepad"
            }
        ]
        
        result = self.run_async(kill_processes_carefully(
            processes=unidentified_processes,
            project_root=str(self.project_root),
            backend_dir=str(self.backend_dir),
            frontend_dir=str(self.frontend_dir),
            logger=logger
        ))
        
        # Should skip unidentified processes
        self.assertIsInstance(result, bool)
        
        # Check that logger was called with warning about skipping
        self.assertTrue(logger.warning.called)

    def test_process_detection_error_handling(self):
        """Test error handling in process detection functions."""
        # Test with invalid project root
        result = self.run_async(is_backend_running("/invalid/path"))
        
        self.assertIsInstance(result, ProcessSearchResult)
        self.assertFalse(result.found)
        self.assertEqual(result.total_count, 0)

    def test_windows_vs_unix_detection(self):
        """Test that platform-specific detection works."""
        import sys
        
        # The functions should work regardless of platform
        # but may have different implementation paths
        result = self.run_async(is_backend_running(str(self.project_root)))
        self.assertIsInstance(result, ProcessSearchResult)
        
        result = self.run_async(is_frontend_running(str(self.project_root)))
        self.assertIsInstance(result, ProcessSearchResult)

    def test_process_search_result_attributes(self):
        """Test all attributes of ProcessSearchResult."""
        processes = [
            {"pid": 1, "name": "proc1"},
            {"pid": 2, "name": "proc2"}
        ]
        
        result = ProcessSearchResult(
            found=True,
            processes=processes,
            total_count=2
        )
        
        # Check all attributes are accessible
        self.assertTrue(hasattr(result, 'found'))
        self.assertTrue(hasattr(result, 'processes'))
        self.assertTrue(hasattr(result, 'total_count'))
        
        # Check values
        self.assertTrue(result.found)
        self.assertEqual(len(result.processes), 2)
        self.assertEqual(result.total_count, 2)

    def test_kill_process_exception_handling(self):
        """Test exception handling in kill_process function."""
        # Test with extreme values
        result = self.run_async(kill_process(-1))
        self.assertFalse(result)
        
        result = self.run_async(kill_process(0))
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
