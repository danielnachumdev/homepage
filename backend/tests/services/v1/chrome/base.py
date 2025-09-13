"""
Base test class for Chrome service testing.
"""
from backend.src.services.v1.chrome_service import ChromeService
from backend.tests.services.v1.base import BaseServiceTest


class CloseChromeTabContext:
    def __init__(self):
        self.chrome_service = ChromeService()

    def __enter__(self):
        self.before = set(h.pid for h in self.chrome_service.get_opened_processes())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        after = set(h.pid for h in self.chrome_service.get_opened_processes())
        diff = after - self.before
        for pid in diff:
            pass  # KILL PID USING SYSTEM GATEWAY OR CHROME SERVICE HANDLER METHOD


class BaseChromeServiceTest(BaseServiceTest):
    """Base test class for Chrome service tests."""
    AutoCloseTabContext = CloseChromeTabContext


__all__ = [
    "BaseChromeServiceTest"
]
