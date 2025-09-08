"""
Tests for SpeedTestService.
"""
import asyncio
from unittest.mock import patch
from .base_test import BaseSpeedTestServiceTest
from backend.src.services.v1.speedtest_service import SpeedTestService
from backend.src.schemas.v1.speedtest import SpeedTestRequest, SpeedTestResult


class TestSpeedTestService(BaseSpeedTestServiceTest):
    """Test the SpeedTestService class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SpeedTestService()

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service.logger)
        self.assertIsNotNone(self.service._current_config)
        self.assertIsNone(self.service._speedtest_instance)
        self.assertIsNone(self.service._last_result)
        self.assertIsNone(self.service._test_task)

    def test_initial_config(self):
        """Test initial configuration values."""
        config = self.service._current_config
        self.assertEqual(config["interval_seconds"], 1)
        self.assertTrue(config["auto_start"])
        self.assertFalse(config["is_running"])

    async def test_perform_speed_test_success(self):
        """Test successful speed test execution."""
        result = await self.service.perform_speed_test()

        self.assertTrue(result.success)
        self.assertIsNotNone(result.result)
        self.assertIn("completed successfully", result.message)

        # Verify the result structure
        speed_result = result.result
        self.assertIsInstance(speed_result, SpeedTestResult)
        self.assertIsNotNone(speed_result.timestamp)
        self.assertTrue(speed_result.is_download_complete)
        self.assertTrue(speed_result.is_upload_complete)
        self.assertTrue(speed_result.is_ping_complete)
        self.assertEqual(speed_result.download_speed_mbps, 50.0)  # 50 Mbps
        self.assertEqual(speed_result.upload_speed_mbps, 10.0)    # 10 Mbps
        self.assertEqual(speed_result.ping_ms, 25.5)
        self.assertEqual(speed_result.server_name, "Test Server")
        self.assertEqual(speed_result.server_sponsor, "Test Sponsor")

        # Verify last result was stored
        self.assertEqual(self.service._last_result, speed_result)

    async def test_perform_speed_test_with_request(self):
        """Test speed test with custom request."""
        request = SpeedTestRequest(interval_seconds=5)
        result = await self.service.perform_speed_test(request)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.result)

    async def test_perform_speed_test_exception(self):
        """Test speed test with exception."""
        # Make the speedtest instance raise an exception
        self.mock_speedtest_instance.get_best_server.side_effect = Exception(
            "Network error")

        result = await self.service.perform_speed_test()

        self.assertFalse(result.success)
        self.assertIsNone(result.result)
        self.assertIn("Error performing speed test", result.message)

    def test_run_speedtest_blocking(self):
        """Test the blocking speedtest execution."""
        result = self.service._run_speedtest_blocking()

        self.assertIsInstance(result, SpeedTestResult)
        self.assertIsNotNone(result.timestamp)
        self.assertTrue(result.is_download_complete)
        self.assertTrue(result.is_upload_complete)
        self.assertTrue(result.is_ping_complete)
        self.assertEqual(result.download_speed_mbps, 50.0)
        self.assertEqual(result.upload_speed_mbps, 10.0)
        self.assertEqual(result.ping_ms, 25.5)
        self.assertEqual(result.server_name, "Test Server")
        self.assertEqual(result.server_sponsor, "Test Sponsor")

    async def test_start_continuous_testing_success(self):
        """Test starting continuous testing successfully."""
        request = SpeedTestRequest(interval_seconds=5)
        result = await self.service.start_continuous_testing(request)

        self.assertTrue(result.success)
        self.assertIn("Started continuous speed testing", result.message)
        self.assertIsNotNone(result.config)
        self.assertEqual(result.config["interval_seconds"], 5)
        self.assertTrue(result.config["is_running"])

        # Verify the task was created
        self.assertIsNotNone(self.service._test_task)
        self.assertFalse(self.service._test_task.done())

    async def test_start_continuous_testing_already_running(self):
        """Test starting continuous testing when already running."""
        # Start testing first
        request = SpeedTestRequest(interval_seconds=5)
        await self.service.start_continuous_testing(request)

        # Try to start again
        result = await self.service.start_continuous_testing(request)

        self.assertFalse(result.success)
        self.assertIn("already running", result.message)

    async def test_stop_continuous_testing_success(self):
        """Test stopping continuous testing successfully."""
        # Start testing first
        request = SpeedTestRequest(interval_seconds=5)
        await self.service.start_continuous_testing(request)

        # Stop testing
        result = await self.service.stop_continuous_testing()

        self.assertTrue(result.success)
        self.assertIn("Stopped continuous speed testing", result.message)
        self.assertIsNotNone(result.config)
        self.assertFalse(result.config["is_running"])

        # Verify the task was cancelled
        self.assertIsNone(self.service._test_task)

    async def test_stop_continuous_testing_not_running(self):
        """Test stopping continuous testing when not running."""
        result = await self.service.stop_continuous_testing()

        self.assertFalse(result.success)
        self.assertIn("not currently running", result.message)

    async def test_get_current_config(self):
        """Test getting current configuration."""
        result = await self.service.get_current_config()

        self.assertTrue(result.success)
        self.assertIn("Configuration retrieved successfully", result.message)
        self.assertIsNotNone(result.config)
        self.assertEqual(result.config, self.service._current_config)

    async def test_get_last_result_success(self):
        """Test getting last result when available."""
        # Perform a speed test first
        await self.service.perform_speed_test()

        result = await self.service.get_last_result()

        self.assertTrue(result.success)
        self.assertIsNotNone(result.result)
        self.assertIn("Last result retrieved successfully", result.message)

    async def test_get_last_result_none(self):
        """Test getting last result when none available."""
        result = await self.service.get_last_result()

        self.assertFalse(result.success)
        self.assertIsNone(result.result)
        self.assertIn("No speed test results available", result.message)

    def test_format_speed(self):
        """Test speed formatting."""
        # Test different speed ranges
        value, unit = self.service.format_speed(500.0)  # 500 Mbps
        self.assertEqual(value, "500.0")
        self.assertEqual(unit, "MB/s")

        value, unit = self.service.format_speed(1500.0)  # 1.5 Gbps
        self.assertEqual(value, "1.5")
        self.assertEqual(unit, "GB/s")

        value, unit = self.service.format_speed(0.5)  # 0.5 Mbps
        self.assertEqual(value, "500")
        self.assertEqual(unit, "KB/s")

    def test_format_ping(self):
        """Test ping formatting."""
        result = self.service.format_ping(25.5)
        self.assertEqual(result, "26 ms")

        result = self.service.format_ping(100.0)
        self.assertEqual(result, "100 ms")

    async def test_continuous_test_loop_cancellation(self):
        """Test continuous test loop cancellation."""
        # Start continuous testing
        # Very short interval for testing
        request = SpeedTestRequest(interval_seconds=0.1)
        await self.service.start_continuous_testing(request)

        # Let it run briefly
        await asyncio.sleep(0.05)

        # Stop it
        result = await self.service.stop_continuous_testing()
        self.assertTrue(result.success)

        # Verify it's stopped
        self.assertFalse(self.service._current_config["is_running"])
        self.assertIsNone(self.service._test_task)

    async def test_continuous_test_loop_exception(self):
        """Test continuous test loop exception handling."""
        # Mock perform_speed_test to raise an exception
        with patch.object(self.service, 'perform_speed_test', side_effect=Exception("Test error")):
            request = SpeedTestRequest(interval_seconds=0.1)
            await self.service.start_continuous_testing(request)

            # Let it run briefly to trigger the exception
            await asyncio.sleep(0.2)

            # Verify it stopped due to exception
            self.assertFalse(self.service._current_config["is_running"])

    async def test_start_continuous_testing_exception(self):
        """Test exception handling in start_continuous_testing."""
        # Mock asyncio.create_task to raise an exception
        with patch('asyncio.create_task', side_effect=Exception("Task creation error")):
            request = SpeedTestRequest(interval_seconds=5)
            result = await self.service.start_continuous_testing(request)

            self.assertFalse(result.success)
            self.assertIn("Error starting continuous testing", result.message)

    async def test_stop_continuous_testing_exception(self):
        """Test exception handling in stop_continuous_testing."""
        # Start testing first
        request = SpeedTestRequest(interval_seconds=5)
        await self.service.start_continuous_testing(request)

        # Mock task.cancel to raise an exception
        with patch.object(self.service._test_task, 'cancel', side_effect=Exception("Cancel error")):
            result = await self.service.stop_continuous_testing()

            self.assertFalse(result.success)
            self.assertIn("Error stopping continuous testing", result.message)


class TestSpeedTestServiceIntegration(BaseSpeedTestServiceTest):
    """Integration tests for SpeedTestService."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SpeedTestService()

    async def test_full_speed_test_workflow(self):
        """Test complete speed test workflow."""
        # 1. Perform initial speed test
        result1 = await self.service.perform_speed_test()
        self.assertTrue(result1.success)

        # 2. Get last result
        last_result = await self.service.get_last_result()
        self.assertTrue(last_result.success)
        self.assertEqual(last_result.result, result1.result)

        # 3. Start continuous testing
        request = SpeedTestRequest(interval_seconds=0.1)
        start_result = await self.service.start_continuous_testing(request)
        self.assertTrue(start_result.success)

        # 4. Let it run for a bit
        await asyncio.sleep(0.3)

        # 5. Stop continuous testing
        stop_result = await self.service.stop_continuous_testing()
        self.assertTrue(stop_result.success)

        # 6. Verify configuration
        config_result = await self.service.get_current_config()
        self.assertTrue(config_result.success)
        self.assertFalse(config_result.config["is_running"])

    async def test_multiple_speed_tests(self):
        """Test performing multiple speed tests."""
        # Perform first test
        result1 = await self.service.perform_speed_test()
        self.assertTrue(result1.success)

        # Perform second test
        result2 = await self.service.perform_speed_test()
        self.assertTrue(result2.success)

        # Verify both results are different (different timestamps)
        self.assertNotEqual(result1.result.timestamp, result2.result.timestamp)

        # Verify last result is the second one
        last_result = await self.service.get_last_result()
        self.assertEqual(last_result.result.timestamp,
                         result2.result.timestamp)

    def test_speed_formatting_edge_cases(self):
        """Test speed formatting edge cases."""
        # Test exactly 1000 Mbps
        value, unit = self.service.format_speed(1000.0)
        self.assertEqual(value, "1.0")
        self.assertEqual(unit, "GB/s")

        # Test exactly 1 Mbps
        value, unit = self.service.format_speed(1.0)
        self.assertEqual(value, "1.0")
        self.assertEqual(unit, "MB/s")

        # Test very small speed
        value, unit = self.service.format_speed(0.001)
        self.assertEqual(value, "1")
        self.assertEqual(unit, "KB/s")

    def test_ping_formatting_edge_cases(self):
        """Test ping formatting edge cases."""
        # Test fractional ping
        result = self.service.format_ping(25.7)
        self.assertEqual(result, "26 ms")

        # Test zero ping
        result = self.service.format_ping(0.0)
        self.assertEqual(result, "0 ms")

        # Test very high ping
        result = self.service.format_ping(999.9)
        self.assertEqual(result, "1000 ms")
