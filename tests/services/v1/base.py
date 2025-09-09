"""
Base test classes for service testing.
"""
from unittest.mock import patch
from typing import Any, Dict, List, Optional
from danielutils.abstractions.db import SelectQuery, UpdateQuery, WhereClause, Condition, Operator

from backend.src.db.database_factory import DatabaseFactory
from ...base import BaseTest


class BaseServiceTest(BaseTest):
    """Base test class for all service tests."""


class BaseDatabaseServiceTest(BaseServiceTest):
    """Base test class for services that use the database."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        # Create an in-memory database for testing
        self.test_db = DatabaseFactory.get_database(db_type="memory")
        self.run_async(self.test_db.connect())
        # Mock the get_db function to return our test database
        self.get_db_patcher = patch('backend.src.db.dependencies.get_db')
        self.mock_get_db = self.get_db_patcher.start()
        self.mock_get_db.return_value = self.test_db

    def tearDown(self):
        """Clean up after each test method."""
        self.get_db_patcher.stop()
        super().tearDown()

    def create_test_setting(
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
        self.run_async(self.test_db.insert("settings", data))
        return data

    def get_test_setting(self, setting_id: str) -> Optional[Dict[str, Any]]:
        """Helper method to get a test setting from the database."""
        where_clause = WhereClause(
            conditions=[
                Condition(column="id", operator=Operator.EQ, value=setting_id)
            ]
        )
        query = SelectQuery(table="settings", where=where_clause)
        records = self.run_async(self.test_db.get(query))
        return records[0] if records else None

    def get_all_test_settings(self) -> List[Dict[str, Any]]:
        """Helper method to get all test settings from the database."""
        query = SelectQuery(table="settings")
        return self.run_async(self.test_db.get(query))

    def update_test_setting(self, setting_id: str, value: Any) -> int:
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
        return self.run_async(self.test_db.update(query))


__all__ = [
    "BaseServiceTest",
    "BaseDatabaseServiceTest"
]
