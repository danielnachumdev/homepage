"""
Tests for SettingsService specific setting methods.
"""
from backend.tests.services.v1.base import BaseDatabaseServiceTest
from backend.src.services.v1.settings_service import SettingsService


class TestSettingsServiceSpecific(BaseDatabaseServiceTest):
    """Test the SettingsService specific setting methods."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = SettingsService()

    def test_update_speed_test_setting(self):
        """Test updating speed test setting."""
        result = self.run_async(self.service.update_speed_test_setting(True))

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

        # Verify the setting was created
        setting = self.get_test_setting("speed_test_enabled")
        self.assertIsNotNone(setting)
        self.assertEqual(setting["category"], "widgets")
        self.assertEqual(setting["setting_type"], "enabled")
        self.assertEqual(setting["value"], {"enabled": True})

    def test_update_search_engine_setting(self):
        """Test updating search engine setting."""
        result = self.run_async(self.service.update_search_engine_setting("google"))

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

        # Verify the setting was created
        setting = self.get_test_setting("search_engine_preference")
        self.assertIsNotNone(setting)
        self.assertEqual(setting["category"], "search_engine")
        self.assertEqual(setting["setting_type"], "engine_preference")
        self.assertEqual(setting["value"], {"selected_engine": "google"})

    def test_update_chrome_profile_setting(self):
        """Test updating Chrome profile setting."""
        result = self.run_async(self.service.update_chrome_profile_setting(
            profile_id="profile1",
            display_name="Work Profile",
            icon="work_icon",
            enabled=True
        ))

        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

        # Verify the setting was created
        setting = self.get_test_setting("chrome_profile_profile1")
        self.assertIsNotNone(setting)
        self.assertEqual(setting["category"], "chrome_profiles")
        self.assertEqual(setting["setting_type"], "profile_display")
        self.assertEqual(setting["value"], {
            "profile_id": "profile1",
            "display_name": "Work Profile",
            "icon": "work_icon",
            "enabled": True
        })
