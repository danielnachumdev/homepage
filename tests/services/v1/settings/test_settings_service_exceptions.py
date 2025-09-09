"""
Tests for SettingsService exception handling.
"""
from unittest.mock import patch
from tests.services.v1.base import BaseDatabaseServiceTest
from backend.src.services.v1.settings_service import SettingsService
from backend.src.schemas.v1.settings import SettingUpdateRequest, BulkSettingsUpdateRequest


class TestSettingsServiceExceptions(BaseDatabaseServiceTest):
    """Test the SettingsService exception handling."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SettingsService()

    def test_get_all_settings_exception_handling(self):
        """Test exception handling in get_all_settings."""
        # Mock database to raise an exception
        with patch.object(self.service.db, 'get', side_effect=Exception("Database error")):
            result = self.run_async(self.service.get_all_settings())

            self.assertFalse(result.success)
            self.assertIn("Error retrieving settings", result.message)
            self.assertEqual(len(result.settings), 0)

    def test_get_setting_exception_handling(self):
        """Test exception handling in get_setting."""
        # Mock database to raise an exception
        with patch.object(self.service.db, 'get', side_effect=Exception("Database error")):
            result = self.run_async(self.service.get_setting("test_setting"))

            self.assertIsNone(result)

    def test_update_setting_exception_handling(self):
        """Test exception handling in update_setting."""
        request = SettingUpdateRequest(id="test_setting", value="new_value")

        # Mock database to raise an exception
        with patch.object(self.service.db, 'update', side_effect=Exception("Database error")):
            result = self.run_async(self.service.update_setting(request))

            self.assertFalse(result.success)
            self.assertIn("Error updating setting", result.message)

    def test_create_or_update_setting_exception_handling(self):
        """Test exception handling in create_or_update_setting."""
        # Mock database to raise an exception
        with patch.object(self.service.db, 'insert', side_effect=Exception("Database error")):
            result = self.run_async(self.service.create_or_update_setting(
                setting_id="test_setting",
                category="category",
                setting_type="type",
                value="value"
            ))

            self.assertFalse(result.success)
            self.assertIn("Error creating/updating setting", result.message)

    def test_bulk_update_settings_exception_handling(self):
        """Test exception handling in bulk_update_settings."""
        request = BulkSettingsUpdateRequest(
            settings=[SettingUpdateRequest(id="setting1", value="value1")]
        )

        # Mock database to raise an exception
        with patch.object(self.service.db, 'get', side_effect=Exception("Database error")):
            result = self.run_async(self.service.bulk_update_settings(request))

            self.assertFalse(result.success)
            self.assertIn("Error in bulk update", result.message)
            self.assertEqual(len(result.failed_updates), 1)
            self.assertIn("Database error", result.failed_updates[0]["error"])
