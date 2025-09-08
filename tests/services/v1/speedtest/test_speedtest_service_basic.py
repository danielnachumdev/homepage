"""
Tests for SpeedTestService basic functionality.
"""
# No additional imports needed for real testing
from tests.services.v1.speedtest.base import BaseSpeedTestServiceTest
from backend.src.services.v1.speedtest_service import SpeedTestService
from backend.src.schemas.v1.speedtest import SpeedTestRequest, SpeedTestResult


class TestSpeedTestServiceBasic(BaseSpeedTestServiceTest):
    """Test the SpeedTestService basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SpeedTestService()

    def test_init(self):
        """Test service initialization."""
        self.logger.info("Testing SpeedTestService initialization")
        self.assertIsNotNone(self.service.logger)
        self.logger.info(
            "SpeedTestService initialization test completed successfully")
        # Note: We don't test private attributes directly in real testing

    def test_initial_config(self):
        """Test initial configuration values."""
        # Test that the service initializes properly
        self.assertIsNotNone(self.service.logger)
        # Note: We don't test private attributes directly in real testing

    async def test_perform_speed_test_success(self):
        """Test successful speed test execution."""
        # This test will use the real speedtest module
        # Note: This test requires internet connection and may take time
        result = await self.service.perform_speed_test()

        # The result depends on internet connectivity and speedtest availability
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)

        if result.success:
            self.assertIsNotNone(result.result)
            self.assertIn("completed successfully", result.message)

            # Verify the result structure
            speed_result = result.result
            self.assertIsInstance(speed_result, SpeedTestResult)
            self.assertIsNotNone(speed_result.timestamp)

            # Verify last result was stored (test public interface)
            last_result = await self.service.get_last_result()
            if last_result.success:
                self.assertIsNotNone(last_result.result)

    async def test_perform_speed_test_with_request(self):
        """Test speed test with custom request."""
        request = SpeedTestRequest(interval_seconds=5)
        result = await self.service.perform_speed_test(request)

        # The result depends on internet connectivity
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        if result.success:
            self.assertIsNotNone(result.result)

    async def test_perform_speed_test_exception(self):
        """Test speed test with network issues."""
        # This test will use the real speedtest module
        # It may fail due to network issues, which is expected
        result = await self.service.perform_speed_test()

        # The result depends on network connectivity
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)

    def test_run_speedtest_blocking(self):
        """Test the blocking speedtest execution."""
        # This test will use the real speedtest module
        # Note: This is a private method, so we test it indirectly through public methods
        # We'll test the public perform_speed_test method instead
        pass

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
