"""
Integration tests for SettingsService.
"""
from backend.tests.services.v1.base import BaseDatabaseServiceTest
from backend.src.services.v1.settings_service import SettingsService


class TestSettingsServiceIntegration(BaseDatabaseServiceTest):
    """Integration tests for SettingsService."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SettingsService()

    def test_complete_settings_workflow(self):
        """Test complete settings management workflow."""
        # 1. Create multiple settings
        self.run_async(self.service.create_or_update_setting(
            "app_name", "general", "string", "My App", "Application name"
        ))
        self.run_async(self.service.create_or_update_setting(
            "max_connections", "database", "integer", 100, "Maximum database connections"
        ))
        self.run_async(self.service.create_or_update_setting(
            "debug_mode", "general", "boolean", False, "Enable debug mode"
        ))

        # 2. Get all settings
        all_settings = self.run_async(self.service.get_all_settings())
        self.assertEqual(len(all_settings.settings), 3)

        # 3. Update a setting
        from backend.src.schemas.v1.settings import SettingUpdateRequest
        update_request = SettingUpdateRequest(id="debug_mode", value=True)
        update_result = self.run_async(self.service.update_setting(update_request))
        self.assertTrue(update_result.success)

        # 4. Verify the update
        updated_setting = self.run_async(self.service.get_setting("debug_mode"))
        self.assertEqual(updated_setting.value, True)

        # 5. Bulk update multiple settings
        from backend.src.schemas.v1.settings import BulkSettingsUpdateRequest
        bulk_request = BulkSettingsUpdateRequest(
            settings=[
                SettingUpdateRequest(id="app_name", value="Updated App"),
                SettingUpdateRequest(id="max_connections", value=200)
            ]
        )
        bulk_result = self.run_async(self.service.bulk_update_settings(bulk_request))
        self.assertTrue(bulk_result.success)

        # 6. Verify bulk updates
        app_setting = self.run_async(self.service.get_setting("app_name"))
        conn_setting = self.run_async(self.service.get_setting("max_connections"))
        self.assertEqual(app_setting.value, "Updated App")
        self.assertEqual(conn_setting.value, 200)

    def test_settings_with_complex_values(self):
        """Test settings with complex data types."""
        # Test with dictionary value
        config_value = {
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "ssl": True
        }

        result = self.run_async(self.service.create_or_update_setting(
            "db_config", "database", "object", config_value, "Database configuration"
        ))

        self.assertTrue(result.success)

        # Retrieve and verify
        retrieved_setting = self.run_async(self.service.get_setting("db_config"))
        self.assertEqual(retrieved_setting.value, config_value)

        # Test with list value
        list_value = ["option1", "option2", "option3"]

        result = self.run_async(self.service.create_or_update_setting(
            "available_options", "ui", "array", list_value, "Available UI options"
        ))

        self.assertTrue(result.success)

        # Retrieve and verify
        retrieved_setting = self.run_async(self.service.get_setting("available_options"))
        self.assertEqual(retrieved_setting.value, list_value)
