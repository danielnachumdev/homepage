"""
Base test class for SpeedTest service testing.
"""
from tests.services.v1.base import BaseServiceTest


class BaseSpeedTestServiceTest(BaseServiceTest):
    """Base test class for SpeedTest service tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        # Use real speedtest module for testing
        # No mocking needed - tests will use actual speedtest functionality


__all__ = [
    "BaseSpeedTestServiceTest"
]
