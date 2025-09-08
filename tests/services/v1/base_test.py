"""
Base test classes for service testing.
"""
import asyncio
import unittest
from unittest.mock import Mock, patch
from typing import Any, Dict, List, Optional
from danielutils.abstractions.db import SelectQuery, UpdateQuery, WhereClause, Condition, Operator

from backend.src.db.database_factory import DatabaseFactory


class BaseServiceTest(unittest.TestCase):
    """Base test class for all service tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up after each test method."""
        self.loop.close()

    def run_async(self, coro):
        """Run an async coroutine in the test loop."""
        return self.loop.run_until_complete(coro)


class BaseDatabaseServiceTest(BaseServiceTest):
    """Base test class for services that use the database."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        # Create an in-memory database for testing
        self.test_db = DatabaseFactory.get_database(db_type="memory")

        # Mock the get_db function to return our test database
        self.get_db_patcher = patch('backend.src.db.dependencies.get_db')
        self.mock_get_db = self.get_db_patcher.start()
        self.mock_get_db.return_value = self.test_db

    def tearDown(self):
        """Clean up after each test method."""
        self.get_db_patcher.stop()
        super().tearDown()

    async def create_test_setting(
        self,
        setting_id: str,
        category: str,
        setting_type: str,
        value: Any,
        description: Optional[str] = None,
        is_user_editable: bool = True
    ) -> Dict[str, Any]:
        """Helper method to create a test setting in the database."""
        data = {
            "id": setting_id,
            "category": category,
            "setting_type": setting_type,
            "value": value,
            "description": description,
            "is_user_editable": str(is_user_editable).lower()
        }
        await self.test_db.insert("settings", data)
        return data

    async def get_test_setting(self, setting_id: str) -> Optional[Dict[str, Any]]:
        """Helper method to get a test setting from the database."""
        where_clause = WhereClause(
            conditions=[
                Condition(column="id", operator=Operator.EQ, value=setting_id)
            ]
        )
        query = SelectQuery(table="settings", where=where_clause)
        records = await self.test_db.get(query)
        return records[0] if records else None

    async def get_all_test_settings(self) -> List[Dict[str, Any]]:
        """Helper method to get all test settings from the database."""
        query = SelectQuery(table="settings")
        return await self.test_db.get(query)

    async def update_test_setting(self, setting_id: str, value: Any) -> int:
        """Helper method to update a test setting in the database."""
        where_clause = WhereClause(
            conditions=[
                Condition(column="id", operator=Operator.EQ, value=setting_id)
            ]
        )
        query = UpdateQuery(
            table="settings",
            where=where_clause,
            data={"value": value}
        )
        return await self.test_db.update(query)


class MockSystemGateway:
    """Mock SystemGateway for testing services that depend on it."""

    def __init__(self):
        self.commands_executed = []
        self.mock_responses = {}

    def set_mock_response(self, command: str, success: bool, output: str = "", error: str = None):
        """Set a mock response for a specific command."""
        self.mock_responses[command] = {
            "success": success,
            "output": output,
            "error": error
        }

    async def execute_command(self, command: str):
        """Mock execute_command method."""
        self.commands_executed.append(command)

        # Look for exact match first
        if command in self.mock_responses:
            response = self.mock_responses[command]
        else:
            # Look for partial matches (useful for commands with dynamic parts)
            for cmd_pattern, response in self.mock_responses.items():
                if cmd_pattern in command:
                    break
            else:
                # Default response
                response = {
                    "success": True,
                    "output": f"Mock output for: {command}",
                    "error": None
                }

        from backend.src.schemas.v1.system import CommandResponse
        return CommandResponse(
            success=response["success"],
            output=response["output"],
            error=response["error"]
        )

    async def execute_command_args(self, command_args: List[str]):
        """Mock execute_command_args method."""
        command = " ".join(command_args)
        return await self.execute_command(command)

    async def execute_multiple_commands(self, commands: List[str]):
        """Mock execute_multiple_commands method."""
        results = []
        for command in commands:
            result = await self.execute_command(command)
            results.append(result)
        return results


class BaseChromeServiceTest(BaseServiceTest):
    """Base test class for Chrome service tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.mock_system_gateway = MockSystemGateway()

        # Mock the SystemGateway import
        self.system_gateway_patcher = patch(
            'backend.src.services.v1.chrome_service.SystemGateway')
        self.mock_system_gateway_class = self.system_gateway_patcher.start()
        self.mock_system_gateway_class.return_value = self.mock_system_gateway

    def tearDown(self):
        """Clean up after each test method."""
        self.system_gateway_patcher.stop()
        super().tearDown()


class BaseDockerServiceTest(BaseServiceTest):
    """Base test class for Docker service tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.mock_system_gateway = MockSystemGateway()

        # Mock the SystemGateway import
        self.system_gateway_patcher = patch(
            'backend.src.services.v1.docker_service.SystemGateway')
        self.mock_system_gateway_class = self.system_gateway_patcher.start()
        self.mock_system_gateway_class.return_value = self.mock_system_gateway

    def tearDown(self):
        """Clean up after each test method."""
        self.system_gateway_patcher.stop()
        super().tearDown()


class BaseSpeedTestServiceTest(BaseServiceTest):
    """Base test class for SpeedTest service tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()

        # Mock the speedtest module
        self.speedtest_patcher = patch(
            'backend.src.services.v1.speedtest_service.speedtest')
        self.mock_speedtest = self.speedtest_patcher.start()

        # Create a mock Speedtest instance
        self.mock_speedtest_instance = Mock()
        self.mock_speedtest.Speedtest.return_value = self.mock_speedtest_instance

        # Set up default mock responses
        self.mock_speedtest_instance.results.server = {
            'name': 'Test Server',
            'sponsor': 'Test Sponsor'
        }
        self.mock_speedtest_instance.results.ping = 25.5
        self.mock_speedtest_instance.download.return_value = 50_000_000  # 50 Mbps in bytes
        self.mock_speedtest_instance.upload.return_value = 10_000_000   # 10 Mbps in bytes

    def tearDown(self):
        """Clean up after each test method."""
        self.speedtest_patcher.stop()
        super().tearDown()
