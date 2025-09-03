import asyncio
import speedtest
from datetime import datetime
from typing import Optional, Dict, Any
from ...schemas.v1.speedtest import (
    SpeedTestRequest, SpeedTestResult, SpeedTestResponse,
    SpeedTestConfigResponse
)
from ...utils.logger import get_logger


class SpeedTestService:
    """Service for performing internet speed tests."""

    def __init__(self):
        self.logger = get_logger("SpeedTestService")
        self._current_config: Dict[str, Any] = {
            "interval_seconds": 1,
            "auto_start": True,
            "is_running": False
        }
        self._speedtest_instance: Optional[speedtest.Speedtest] = None
        self._last_result: Optional[SpeedTestResult] = None
        self._test_task: Optional[asyncio.Task] = None

    async def perform_speed_test(self, request: Optional[SpeedTestRequest] = None) -> SpeedTestResponse:
        """Perform a single speed test with partial results."""
        try:
            self.logger.info("Starting speed test...")

            # Run the blocking speedtest operations in a separate thread
            result = await asyncio.to_thread(self._run_speedtest_blocking)

            self._last_result = result
            self.logger.info(
                f"Speed test completed: {result.download_speed_mbps:.2f} Mbps down, {result.upload_speed_mbps:.2f} Mbps up, {result.ping_ms:.2f} ms ping")

            return SpeedTestResponse(
                success=True,
                result=result,
                message="Speed test completed successfully"
            )

        except Exception as e:
            self.logger.error(f"Error performing speed test: {str(e)}")
            return SpeedTestResponse(
                success=False,
                message=f"Error performing speed test: {str(e)}"
            )

    def _run_speedtest_blocking(self) -> SpeedTestResult:
        """Run the blocking speedtest operations in a separate thread."""
        # Create speedtest instance
        st = speedtest.Speedtest()

        # Initialize result with server info
        result = SpeedTestResult(
            timestamp=datetime.now(),
            is_download_complete=False,
            is_upload_complete=False,
            is_ping_complete=False
        )

        # Get the best server based on ping
        self.logger.info("Finding best server...")
        st.get_best_server()

        server_name = st.results.server.get('name', 'Unknown')
        server_sponsor = st.results.server.get('sponsor', 'Unknown')
        result.server_name = server_name
        result.server_sponsor = server_sponsor

        self.logger.info(
            f"Testing against server: {server_sponsor} ({server_name})")

        # Get ping first (usually fastest)
        self.logger.info("Testing ping...")
        ping = st.results.ping
        result.ping_ms = ping
        result.is_ping_complete = True

        # Test download speed
        self.logger.info("Testing download speed...")
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        result.download_speed_mbps = download_speed
        result.is_download_complete = True

        # Test upload speed
        self.logger.info("Testing upload speed...")
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        result.upload_speed_mbps = upload_speed
        result.is_upload_complete = True

        return result

    async def start_continuous_testing(self, request: SpeedTestRequest) -> SpeedTestConfigResponse:
        """Start continuous speed testing with specified interval."""
        try:
            if self._current_config["is_running"]:
                return SpeedTestConfigResponse(
                    success=False,
                    message="Speed testing is already running"
                )

            # Update configuration
            self._current_config.update({
                "interval_seconds": request.interval_seconds,
                "is_running": True
            })

            # Start the continuous testing task
            self._test_task = asyncio.create_task(self._continuous_test_loop())

            self.logger.info(
                f"Started continuous speed testing with {request.interval_seconds}s interval")

            return SpeedTestConfigResponse(
                success=True,
                message=f"Started continuous speed testing with {request.interval_seconds}s interval",
                config=self._current_config.copy()
            )

        except Exception as e:
            self.logger.error(f"Error starting continuous testing: {str(e)}")
            return SpeedTestConfigResponse(
                success=False,
                message=f"Error starting continuous testing: {str(e)}"
            )

    async def stop_continuous_testing(self) -> SpeedTestConfigResponse:
        """Stop continuous speed testing."""
        try:
            if not self._current_config["is_running"]:
                return SpeedTestConfigResponse(
                    success=False,
                    message="Speed testing is not currently running"
                )

            # Cancel the test task
            if self._test_task and not self._test_task.done():
                self._test_task.cancel()
                try:
                    await self._test_task
                except asyncio.CancelledError:
                    pass

            # Update configuration
            self._current_config["is_running"] = False
            self._test_task = None

            self.logger.info("Stopped continuous speed testing")

            return SpeedTestConfigResponse(
                success=True,
                message="Stopped continuous speed testing",
                config=self._current_config.copy()
            )

        except Exception as e:
            self.logger.error(f"Error stopping continuous testing: {str(e)}")
            return SpeedTestConfigResponse(
                success=False,
                message=f"Error stopping continuous testing: {str(e)}"
            )

    async def get_current_config(self) -> SpeedTestConfigResponse:
        """Get current speed test configuration."""
        return SpeedTestConfigResponse(
            success=True,
            message="Configuration retrieved successfully",
            config=self._current_config.copy()
        )

    async def get_last_result(self) -> SpeedTestResponse:
        """Get the last speed test result."""
        if self._last_result is None:
            return SpeedTestResponse(
                success=False,
                message="No speed test results available"
            )

        return SpeedTestResponse(
            success=True,
            result=self._last_result,
            message="Last result retrieved successfully"
        )

    async def _continuous_test_loop(self):
        """Internal method to run continuous speed tests."""
        try:
            while self._current_config["is_running"]:
                # Perform a speed test (already uses asyncio.to_thread internally)
                await self.perform_speed_test()

                # Wait for the specified interval
                await asyncio.sleep(self._current_config["interval_seconds"])

        except asyncio.CancelledError:
            self.logger.info("Continuous testing loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Error in continuous testing loop: {str(e)}")
            self._current_config["is_running"] = False

    def format_speed(self, speed_mbps: float) -> tuple[str, str]:
        """Format speed value to appropriate unit and return (value, unit)."""
        if speed_mbps >= 1000:
            return f"{speed_mbps / 1000:.1f}", "GB/s"
        elif speed_mbps >= 1:
            return f"{speed_mbps:.1f}", "MB/s"
        else:
            return f"{speed_mbps * 1000:.0f}", "KB/s"

    def format_ping(self, ping_ms: float) -> str:
        """Format ping value."""
        return f"{ping_ms:.0f} ms"


__all__ = [
    "SpeedTestService"
]
