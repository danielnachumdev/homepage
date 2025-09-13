"""
Base test class for Docker service testing.
"""
from backend.tests.services.v1.base import BaseServiceTest


class BaseDockerServiceTest(BaseServiceTest):
    """Base test class for Docker service tests."""


__all__ = [
    "BaseDockerServiceTest"
]
