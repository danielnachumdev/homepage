"""
Integration tests for SpeedTestService.
"""
import asyncio
from tests.services.v1.speedtest.base import BaseSpeedTestServiceTest
from backend.src.services.v1.speedtest_service import SpeedTestService
from backend.src.schemas.v1.speedtest import SpeedTestRequest


class TestSpeedTestServiceIntegration(BaseSpeedTestServiceTest):
    """Integration tests for SpeedTestService."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SpeedTestService()

    def test_full_speed_test_workflow(self):
        """Test complete speed test workflow."""
        # 1. Perform initial speed test
        result1 = self.run_async(self.service.perform_speed_test())
        self.assertTrue(result1.success)

        # 2. Get last result
        last_result = self.run_async(self.service.get_last_result())
        self.assertTrue(last_result.success)
        self.assertEqual(last_result.result, result1.result)

        # 3. Start continuous testing
        request = SpeedTestRequest(interval_seconds=0.1)
        start_result = self.run_async(self.service.start_continuous_testing(request))
        self.assertTrue(start_result.success)

        # 4. Let it run for a bit
        self.run_async(asyncio.sleep(0.3))

        # 5. Stop continuous testing
        stop_result = self.run_async(self.service.stop_continuous_testing())
        self.assertTrue(stop_result.success)

        # 6. Verify configuration
        config_result = self.run_async(self.service.get_current_config())
        self.assertTrue(config_result.success)
        self.assertFalse(config_result.config["is_running"])

    def test_multiple_speed_tests(self):
        """Test performing multiple speed tests."""
        # Perform first test
        result1 = self.run_async(self.service.perform_speed_test())
        self.assertTrue(result1.success)

        # Perform second test
        result2 = self.run_async(self.service.perform_speed_test())
        self.assertTrue(result2.success)

        # Verify both results are different (different timestamps)
        self.assertNotEqual(result1.result.timestamp, result2.result.timestamp)

        # Verify last result is the second one
        last_result = self.run_async(self.service.get_last_result())
        self.assertEqual(last_result.result.timestamp, result2.result.timestamp)

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
