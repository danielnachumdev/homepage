"""
Tests for SettingsService CRUD operations.
"""
from unittest.mock import patch
from backend.src.services.v1.settings_service import SettingsService
from backend.src.schemas.v1.settings import SettingValue, SettingUpdateRequest, BulkSettingsUpdateRequest
from ..base import BaseDatabaseServiceTest


class TestSettingsServiceCRUD(BaseDatabaseServiceTest):
    """Test the SettingsService CRUD operations."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SettingsService()

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service.logger)
        self.assertIsNotNone(self.service.db)

    def test_get_all_settings_empty(self):
        """Test getting all settings when database is empty."""
        result = self.run_async(self.service.get_all_settings())

        self.assertTrue(result.success)
        self.assertEqual(len(result.settings), 0)
        self.assertIn("Retrieved 0 settings", result.message)

    def test_get_all_settings_with_data(self):
        """Test getting all settings with data in database."""
        # Create test settings
        self.create_test_setting("test_setting_1", "category1", "type1", "value1", "Description 1")
        self.create_test_setting("test_setting_2", "category2", "type2", "value2", "Description 2")

        result = self.run_async(self.service.get_all_settings())

        self.assertTrue(result.success)
        self.assertEqual(len(result.settings), 2)
        self.assertIn("Retrieved 2 settings", result.message)

        # Check that settings are properly converted to SettingValue objects
        setting_ids = [s.id for s in result.settings]
        self.assertIn("test_setting_1", setting_ids)
        self.assertIn("test_setting_2", setting_ids)

    def test_get_setting_success(self):
        """Test getting a specific setting successfully."""
        # Create test setting
        self.create_test_setting("test_setting", "category", "type", "value", "Description")

        result = self.run_async(self.service.get_setting("test_setting"))

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SettingValue)
        self.assertEqual(result.id, "test_setting")
        self.assertEqual(result.category, "category")
        self.assertEqual(result.setting_type, "type")
        self.assertEqual(result.value, "value")
        self.assertEqual(result.description, "Description")

    def test_get_setting_not_found(self):
        """Test getting a setting that doesn't exist."""
        result = self.run_async(self.service.get_setting("nonexistent_setting"))
        self.assertIsNone(result)

    def test_update_setting_success(self):
        """Test successful setting update."""
        # Create test setting
        self.create_test_setting("test_setting", "category", "type", "old_value", "Description")

        request = SettingUpdateRequest(id="test_setting", value="new_value")
        result = self.run_async(self.service.update_setting(request))

        self.assertTrue(result.success)
        self.assertIn("updated successfully", result.message)
        self.assertIsNotNone(result.setting)
        self.assertEqual(result.setting.value, "new_value")

        # Verify the setting was actually updated in the database
        updated_setting = self.get_test_setting("test_setting")
        self.assertEqual(updated_setting["value"], "new_value")

    def test_update_setting_not_found(self):
        """Test updating a setting that doesn't exist."""
        request = SettingUpdateRequest(id="nonexistent_setting", value="new_value")
        result = self.run_async(self.service.update_setting(request))

        self.assertFalse(result.success)
        self.assertIn("not found", result.message)
        self.assertIsNone(result.setting)

    def test_create_or_update_setting_create_new(self):
        """Test creating a new setting."""
        result = self.run_async(self.service.create_or_update_setting(
            setting_id="new_setting",
            category="test_category",
            setting_type="test_type",
            value="test_value",
            description="Test description",
            is_user_editable=True
        ))

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)
        self.assertIsNotNone(result.setting)
        self.assertEqual(result.setting.id, "new_setting")
        self.assertEqual(result.setting.value, "test_value")

        # Verify the setting was created in the database
        created_setting = self.get_test_setting("new_setting")
        self.assertIsNotNone(created_setting)
        self.assertEqual(created_setting["value"], "test_value")

    def test_create_or_update_setting_update_existing(self):
        """Test updating an existing setting."""
        # Create initial setting
        self.create_test_setting("existing_setting", "category", "type", "old_value", "Old description")

        result = self.run_async(self.service.create_or_update_setting(
            setting_id="existing_setting",
            category="updated_category",
            setting_type="updated_type",
            value="new_value",
            description="New description",
            is_user_editable=False
        ))

        self.assertTrue(result.success)
        self.assertIn("updated successfully", result.message)
        self.assertIsNotNone(result.setting)
        self.assertEqual(result.setting.value, "new_value")
        self.assertEqual(result.setting.description, "New description")

        # Verify the setting was updated in the database
        updated_setting = self.get_test_setting("existing_setting")
        self.assertEqual(updated_setting["value"], "new_value")
        self.assertEqual(updated_setting["description"], "New description")
        self.assertEqual(updated_setting["is_user_editable"], "false")

    def test_bulk_update_settings_success(self):
        """Test successful bulk settings update."""
        # Create test settings
        self.create_test_setting("setting1", "category", "type", "old_value1")
        self.create_test_setting("setting2", "category", "type", "old_value2")

        request = BulkSettingsUpdateRequest(
            settings=[
                SettingUpdateRequest(id="setting1", value="new_value1"),
                SettingUpdateRequest(id="setting2", value="new_value2")
            ]
        )

        result = self.run_async(self.service.bulk_update_settings(request))

        self.assertTrue(result.success)
        self.assertEqual(len(result.updated_settings), 2)
        self.assertEqual(len(result.failed_updates), 0)
        self.assertIn("Updated 2 settings, 0 failed", result.message)

        # Verify settings were updated
        setting1 = self.get_test_setting("setting1")
        setting2 = self.get_test_setting("setting2")
        self.assertEqual(setting1["value"], "new_value1")
        self.assertEqual(setting2["value"], "new_value2")

    def test_bulk_update_settings_partial_failure(self):
        """Test bulk update with some failures."""
        # Create only one test setting
        self.create_test_setting("setting1", "category", "type", "old_value1")

        request = BulkSettingsUpdateRequest(
            settings=[
                SettingUpdateRequest(id="setting1", value="new_value1"),
                SettingUpdateRequest(
                    id="nonexistent_setting", value="new_value2")
            ]
        )

        result = self.run_async(self.service.bulk_update_settings(request))

        self.assertFalse(result.success)
        self.assertEqual(len(result.updated_settings), 1)
        self.assertEqual(len(result.failed_updates), 1)
        self.assertIn("Updated 1 settings, 1 failed", result.message)

        # Check failed update details
        failed_update = result.failed_updates[0]
        self.assertEqual(failed_update["id"], "nonexistent_setting")
        self.assertIn("Setting not found", failed_update["error"])
