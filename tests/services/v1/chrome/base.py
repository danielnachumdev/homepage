"""
Base test class for Chrome service testing.
"""
from tests.services.v1.base import BaseServiceTest
from backend.src.gateways.v1.system_gateway import SystemGateway


class BaseChromeServiceTest(BaseServiceTest):
    """Base test class for Chrome service tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        # Use real SystemGateway for testing
        self.system_gateway = SystemGateway()

    def tearDown(self):
        """Clean up after each test method."""
        super().tearDown()


__all__ = [
    "BaseChromeServiceTest"
]
