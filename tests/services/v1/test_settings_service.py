"""
Tests for SettingsService.
"""
from unittest.mock import patch
from .base_test import BaseDatabaseServiceTest
from backend.src.services.v1.settings_service import SettingsService
from backend.src.schemas.v1.settings import (
    SettingValue, SettingUpdateRequest, BulkSettingsUpdateRequest
)


class TestSettingsService(BaseDatabaseServiceTest):
    """Test the SettingsService class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SettingsService()

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service.logger)
        self.assertIsNotNone(self.service.db)

    async def test_get_all_settings_empty(self):
        """Test getting all settings when database is empty."""
        result = await self.service.get_all_settings()

        self.assertTrue(result.success)
        self.assertEqual(len(result.settings), 0)
        self.assertIn("Retrieved 0 settings", result.message)

    async def test_get_all_settings_with_data(self):
        """Test getting all settings with data in database."""
        # Create test settings
        await self.create_test_setting(
            "test_setting_1", "category1", "type1", "value1", "Description 1"
        )
        await self.create_test_setting(
            "test_setting_2", "category2", "type2", "value2", "Description 2"
        )

        result = await self.service.get_all_settings()

        self.assertTrue(result.success)
        self.assertEqual(len(result.settings), 2)
        self.assertIn("Retrieved 2 settings", result.message)

        # Check that settings are properly converted to SettingValue objects
        setting_ids = [s.id for s in result.settings]
        self.assertIn("test_setting_1", setting_ids)
        self.assertIn("test_setting_2", setting_ids)

    async def test_get_setting_success(self):
        """Test getting a specific setting successfully."""
        # Create test setting
        await self.create_test_setting(
            "test_setting", "category", "type", "value", "Description"
        )

        result = await self.service.get_setting("test_setting")

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SettingValue)
        self.assertEqual(result.id, "test_setting")
        self.assertEqual(result.category, "category")
        self.assertEqual(result.setting_type, "type")
        self.assertEqual(result.value, "value")
        self.assertEqual(result.description, "Description")

    async def test_get_setting_not_found(self):
        """Test getting a setting that doesn't exist."""
        result = await self.service.get_setting("nonexistent_setting")
        self.assertIsNone(result)

    async def test_update_setting_success(self):
        """Test successful setting update."""
        # Create test setting
        await self.create_test_setting(
            "test_setting", "category", "type", "old_value", "Description"
        )

        request = SettingUpdateRequest(id="test_setting", value="new_value")
        result = await self.service.update_setting(request)

        self.assertTrue(result.success)
        self.assertIn("updated successfully", result.message)
        self.assertIsNotNone(result.setting)
        self.assertEqual(result.setting.value, "new_value")

        # Verify the setting was actually updated in the database
        updated_setting = await self.get_test_setting("test_setting")
        self.assertEqual(updated_setting["value"], "new_value")

    async def test_update_setting_not_found(self):
        """Test updating a setting that doesn't exist."""
        request = SettingUpdateRequest(
            id="nonexistent_setting", value="new_value")
        result = await self.service.update_setting(request)

        self.assertFalse(result.success)
        self.assertIn("not found", result.message)
        self.assertIsNone(result.setting)

    async def test_create_or_update_setting_create_new(self):
        """Test creating a new setting."""
        result = await self.service.create_or_update_setting(
            setting_id="new_setting",
            category="test_category",
            setting_type="test_type",
            value="test_value",
            description="Test description",
            is_user_editable=True
        )

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)
        self.assertIsNotNone(result.setting)
        self.assertEqual(result.setting.id, "new_setting")
        self.assertEqual(result.setting.value, "test_value")

        # Verify the setting was created in the database
        created_setting = await self.get_test_setting("new_setting")
        self.assertIsNotNone(created_setting)
        self.assertEqual(created_setting["value"], "test_value")

    async def test_create_or_update_setting_update_existing(self):
        """Test updating an existing setting."""
        # Create initial setting
        await self.create_test_setting(
            "existing_setting", "category", "type", "old_value", "Old description"
        )

        result = await self.service.create_or_update_setting(
            setting_id="existing_setting",
            category="updated_category",
            setting_type="updated_type",
            value="new_value",
            description="New description",
            is_user_editable=False
        )

        self.assertTrue(result.success)
        self.assertIn("updated successfully", result.message)
        self.assertIsNotNone(result.setting)
        self.assertEqual(result.setting.value, "new_value")
        self.assertEqual(result.setting.description, "New description")

        # Verify the setting was updated in the database
        updated_setting = await self.get_test_setting("existing_setting")
        self.assertEqual(updated_setting["value"], "new_value")
        self.assertEqual(updated_setting["description"], "New description")
        self.assertEqual(updated_setting["is_user_editable"], "false")

    async def test_bulk_update_settings_success(self):
        """Test successful bulk settings update."""
        # Create test settings
        await self.create_test_setting("setting1", "category", "type", "old_value1")
        await self.create_test_setting("setting2", "category", "type", "old_value2")

        request = BulkSettingsUpdateRequest(
            settings=[
                SettingUpdateRequest(id="setting1", value="new_value1"),
                SettingUpdateRequest(id="setting2", value="new_value2")
            ]
        )

        result = await self.service.bulk_update_settings(request)

        self.assertTrue(result.success)
        self.assertEqual(len(result.updated_settings), 2)
        self.assertEqual(len(result.failed_updates), 0)
        self.assertIn("Updated 2 settings, 0 failed", result.message)

        # Verify settings were updated
        setting1 = await self.get_test_setting("setting1")
        setting2 = await self.get_test_setting("setting2")
        self.assertEqual(setting1["value"], "new_value1")
        self.assertEqual(setting2["value"], "new_value2")

    async def test_bulk_update_settings_partial_failure(self):
        """Test bulk update with some failures."""
        # Create only one test setting
        await self.create_test_setting("setting1", "category", "type", "old_value1")

        request = BulkSettingsUpdateRequest(
            settings=[
                SettingUpdateRequest(id="setting1", value="new_value1"),
                SettingUpdateRequest(
                    id="nonexistent_setting", value="new_value2")
            ]
        )

        result = await self.service.bulk_update_settings(request)

        self.assertFalse(result.success)
        self.assertEqual(len(result.updated_settings), 1)
        self.assertEqual(len(result.failed_updates), 1)
        self.assertIn("Updated 1 settings, 1 failed", result.message)

        # Check failed update details
        failed_update = result.failed_updates[0]
        self.assertEqual(failed_update["id"], "nonexistent_setting")
        self.assertIn("Setting not found", failed_update["error"])

    async def test_update_speed_test_setting(self):
        """Test updating speed test setting."""
        result = await self.service.update_speed_test_setting(True)

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

        # Verify the setting was created
        setting = await self.get_test_setting("speed_test_enabled")
        self.assertIsNotNone(setting)
        self.assertEqual(setting["category"], "widgets")
        self.assertEqual(setting["setting_type"], "enabled")
        self.assertEqual(setting["value"], {"enabled": True})

    async def test_update_search_engine_setting(self):
        """Test updating search engine setting."""
        result = await self.service.update_search_engine_setting("google")

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

        # Verify the setting was created
        setting = await self.get_test_setting("search_engine_preference")
        self.assertIsNotNone(setting)
        self.assertEqual(setting["category"], "search_engine")
        self.assertEqual(setting["setting_type"], "engine_preference")
        self.assertEqual(setting["value"], {"selected_engine": "google"})

    async def test_update_chrome_profile_setting(self):
        """Test updating Chrome profile setting."""
        result = await self.service.update_chrome_profile_setting(
            profile_id="profile1",
            display_name="Work Profile",
            icon="work_icon",
            enabled=True
        )

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

        # Verify the setting was created
        setting = await self.get_test_setting("chrome_profile_profile1")
        self.assertIsNotNone(setting)
        self.assertEqual(setting["category"], "chrome_profiles")
        self.assertEqual(setting["setting_type"], "profile_display")
        self.assertEqual(setting["value"], {
            "profile_id": "profile1",
            "display_name": "Work Profile",
            "icon": "work_icon",
            "enabled": True
        })

    async def test_get_all_settings_exception_handling(self):
        """Test exception handling in get_all_settings."""
        # Mock database to raise an exception
        with patch.object(self.service.db, 'get', side_effect=Exception("Database error")):
            result = await self.service.get_all_settings()

            self.assertFalse(result.success)
            self.assertIn("Error retrieving settings", result.message)
            self.assertEqual(len(result.settings), 0)

    async def test_get_setting_exception_handling(self):
        """Test exception handling in get_setting."""
        # Mock database to raise an exception
        with patch.object(self.service.db, 'get', side_effect=Exception("Database error")):
            result = await self.service.get_setting("test_setting")

            self.assertIsNone(result)

    async def test_update_setting_exception_handling(self):
        """Test exception handling in update_setting."""
        request = SettingUpdateRequest(id="test_setting", value="new_value")

        # Mock database to raise an exception
        with patch.object(self.service.db, 'update', side_effect=Exception("Database error")):
            result = await self.service.update_setting(request)

            self.assertFalse(result.success)
            self.assertIn("Error updating setting", result.message)

    async def test_create_or_update_setting_exception_handling(self):
        """Test exception handling in create_or_update_setting."""
        # Mock database to raise an exception
        with patch.object(self.service.db, 'insert', side_effect=Exception("Database error")):
            result = await self.service.create_or_update_setting(
                setting_id="test_setting",
                category="category",
                setting_type="type",
                value="value"
            )

            self.assertFalse(result.success)
            self.assertIn("Error creating/updating setting", result.message)

    async def test_bulk_update_settings_exception_handling(self):
        """Test exception handling in bulk_update_settings."""
        request = BulkSettingsUpdateRequest(
            settings=[SettingUpdateRequest(id="setting1", value="value1")]
        )

        # Mock database to raise an exception
        with patch.object(self.service.db, 'get', side_effect=Exception("Database error")):
            result = await self.service.bulk_update_settings(request)

            self.assertFalse(result.success)
            self.assertIn("Error in bulk update", result.message)
            self.assertEqual(len(result.failed_updates), 1)
            self.assertIn("Database error", result.failed_updates[0]["error"])


class TestSettingsServiceIntegration(BaseDatabaseServiceTest):
    """Integration tests for SettingsService."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SettingsService()

    async def test_complete_settings_workflow(self):
        """Test complete settings management workflow."""
        # 1. Create multiple settings
        await self.service.create_or_update_setting(
            "app_name", "general", "string", "My App", "Application name"
        )
        await self.service.create_or_update_setting(
            "max_connections", "database", "integer", 100, "Maximum database connections"
        )
        await self.service.create_or_update_setting(
            "debug_mode", "general", "boolean", False, "Enable debug mode"
        )

        # 2. Get all settings
        all_settings = await self.service.get_all_settings()
        self.assertEqual(len(all_settings.settings), 3)

        # 3. Update a setting
        update_request = SettingUpdateRequest(id="debug_mode", value=True)
        update_result = await self.service.update_setting(update_request)
        self.assertTrue(update_result.success)

        # 4. Verify the update
        updated_setting = await self.service.get_setting("debug_mode")
        self.assertEqual(updated_setting.value, True)

        # 5. Bulk update multiple settings
        bulk_request = BulkSettingsUpdateRequest(
            settings=[
                SettingUpdateRequest(id="app_name", value="Updated App"),
                SettingUpdateRequest(id="max_connections", value=200)
            ]
        )
        bulk_result = await self.service.bulk_update_settings(bulk_request)
        self.assertTrue(bulk_result.success)

        # 6. Verify bulk updates
        app_setting = await self.service.get_setting("app_name")
        conn_setting = await self.service.get_setting("max_connections")
        self.assertEqual(app_setting.value, "Updated App")
        self.assertEqual(conn_setting.value, 200)

    async def test_settings_with_complex_values(self):
        """Test settings with complex data types."""
        # Test with dictionary value
        config_value = {
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "ssl": True
        }

        result = await self.service.create_or_update_setting(
            "db_config", "database", "object", config_value, "Database configuration"
        )

        self.assertTrue(result.success)

        # Retrieve and verify
        retrieved_setting = await self.service.get_setting("db_config")
        self.assertEqual(retrieved_setting.value, config_value)

        # Test with list value
        list_value = ["option1", "option2", "option3"]

        result = await self.service.create_or_update_setting(
            "available_options", "ui", "array", list_value, "Available UI options"
        )

        self.assertTrue(result.success)

        # Retrieve and verify
        retrieved_setting = await self.service.get_setting("available_options")
        self.assertEqual(retrieved_setting.value, list_value)
