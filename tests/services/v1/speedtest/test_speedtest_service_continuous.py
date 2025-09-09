"""
Tests for SpeedTestService continuous testing functionality.
"""
import asyncio
from unittest.mock import patch
from tests.services.v1.speedtest.base import BaseSpeedTestServiceTest
from backend.src.services.v1.speedtest_service import SpeedTestService
from backend.src.schemas.v1.speedtest import SpeedTestRequest


class TestSpeedTestServiceContinuous(BaseSpeedTestServiceTest):
    """Test the SpeedTestService continuous testing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SpeedTestService()

    def test_start_continuous_testing_success(self):
        """Test starting continuous testing successfully."""
        request = SpeedTestRequest(interval_seconds=5)
        result = self.run_async(self.service.start_continuous_testing(request))

        self.assertTrue(result.success)
        self.assertIn("Started continuous speed testing", result.message)
        self.assertIsNotNone(result.config)
        self.assertEqual(result.config["interval_seconds"], 5)
        self.assertTrue(result.config["is_running"])

        # Verify the task was created
        self.assertIsNotNone(self.service._test_task)
        self.assertFalse(self.service._test_task.done())

    def test_start_continuous_testing_already_running(self):
        """Test starting continuous testing when already running."""
        # Start testing first
        request = SpeedTestRequest(interval_seconds=5)
        self.run_async(self.service.start_continuous_testing(request))

        # Try to start again
        result = self.run_async(self.service.start_continuous_testing(request))

        self.assertFalse(result.success)
        self.assertIn("already running", result.message)

    def test_stop_continuous_testing_success(self):
        """Test stopping continuous testing successfully."""
        # Start testing first
        request = SpeedTestRequest(interval_seconds=5)
        self.run_async(self.service.start_continuous_testing(request))

        # Stop testing
        result = self.run_async(self.service.stop_continuous_testing())

        self.assertTrue(result.success)
        self.assertIn("Stopped continuous speed testing", result.message)
        self.assertIsNotNone(result.config)
        self.assertFalse(result.config["is_running"])

        # Verify the task was cancelled
        self.assertIsNone(self.service._test_task)

    def test_stop_continuous_testing_not_running(self):
        """Test stopping continuous testing when not running."""
        result = self.run_async(self.service.stop_continuous_testing())

        self.assertFalse(result.success)
        self.assertIn("not currently running", result.message)

    def test_get_current_config(self):
        """Test getting current configuration."""
        result = self.run_async(self.service.get_current_config())

        self.assertTrue(result.success)
        self.assertIn("Configuration retrieved successfully", result.message)
        self.assertIsNotNone(result.config)
        self.assertEqual(result.config, self.service._current_config)

    def test_get_last_result_success(self):
        """Test getting last result when available."""
        # Perform a speed test first
        self.run_async(self.service.perform_speed_test())

        result = self.run_async(self.service.get_last_result())

        self.assertTrue(result.success)
        self.assertIsNotNone(result.result)
        self.assertIn("Last result retrieved successfully", result.message)

    def test_get_last_result_none(self):
        """Test getting last result when none available."""
        result = self.run_async(self.service.get_last_result())

        self.assertFalse(result.success)
        self.assertIsNone(result.result)
        self.assertIn("No speed test results available", result.message)

    def test_continuous_test_loop_cancellation(self):
        """Test continuous test loop cancellation."""
        # Start continuous testing
        # Very short interval for testing
        request = SpeedTestRequest(interval_seconds=0.1)
        self.run_async(self.service.start_continuous_testing(request))

        # Let it run briefly
        self.run_async(asyncio.sleep(0.05))

        # Stop it
        result = self.run_async(self.service.stop_continuous_testing())
        self.assertTrue(result.success)

        # Verify it's stopped
        self.assertFalse(self.service._current_config["is_running"])
        self.assertIsNone(self.service._test_task)

    def test_continuous_test_loop_exception(self):
        """Test continuous test loop exception handling."""
        # Mock perform_speed_test to raise an exception
        with patch.object(self.service, 'perform_speed_test', side_effect=Exception("Test error")):
            request = SpeedTestRequest(interval_seconds=0.1)
            self.run_async(self.service.start_continuous_testing(request))

            # Let it run briefly to trigger the exception
            self.run_async(asyncio.sleep(0.2))

            # Verify it stopped due to exception
            self.assertFalse(self.service._current_config["is_running"])

    def test_start_continuous_testing_exception(self):
        """Test exception handling in start_continuous_testing."""
        # Mock asyncio.create_task to raise an exception
        with patch('asyncio.create_task', side_effect=Exception("Task creation error")):
            request = SpeedTestRequest(interval_seconds=5)
            result = self.run_async(self.service.start_continuous_testing(request))

            self.assertFalse(result.success)
            self.assertIn("Error starting continuous testing", result.message)

    def test_stop_continuous_testing_exception(self):
        """Test exception handling in stop_continuous_testing."""
        # Start testing first
        request = SpeedTestRequest(interval_seconds=5)
        self.run_async(self.service.start_continuous_testing(request))

        # Mock task.cancel to raise an exception
        with patch.object(self.service._test_task, 'cancel', side_effect=Exception("Cancel error")):
            result = self.run_async(self.service.stop_continuous_testing())

            self.assertFalse(result.success)
            self.assertIn("Error stopping continuous testing", result.message)
