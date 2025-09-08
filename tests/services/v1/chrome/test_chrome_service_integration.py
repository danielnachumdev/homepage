"""
Integration tests for ChromeService.
"""
import os
import json
import tempfile
from unittest.mock import patch
from tests.services.v1.chrome.base import BaseChromeServiceTest
from backend.src.services.v1.chrome_service import ChromeService, extract_jsonpath_value
from backend.src.schemas.v1.chrome import ChromeProfile, ChromeProfileInfo


class TestChromeServiceIntegration(BaseChromeServiceTest):
    """Integration tests for ChromeService."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = ChromeService()

    def test_full_profile_extraction_workflow(self):
        """Test the complete workflow of profile extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a realistic Preferences file
            preferences_data = {
                "profile": {"name": "Work Profile"},
                "account_info": [{
                    "account_id": "work_account_123",
                    "email": "work@company.com",
                    "full_name": "John Doe",
                    "given_name": "John",
                    "picture_url": "https://lh3.googleusercontent.com/photo.jpg",
                    "locale": "en-US"
                }],
                "extensions": {
                    "settings": {}
                },
                "browser": {
                    "has_seen_welcome_page": True
                }
            }

            preferences_file = os.path.join(temp_dir, "Preferences")
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences_data, f)

            # Extract profile information
            result = self.service._extract_profile_information(temp_dir)

            # Verify the result
            self.assertIsNotNone(result)
            self.assertEqual(result.profile_name, "Work Profile")
            self.assertEqual(result.email, "work@company.com")
            self.assertEqual(result.full_name, "John Doe")

    def test_chrome_command_with_real_paths(self):
        """Test Chrome command building with realistic paths."""
        profile = ChromeProfile(id="Default", name="Default Profile")
        url = "https://google.com"

        with patch('os.path.exists') as mock_exists:
            # Mock Chrome found in Program Files
            def exists_side_effect(path):
                return path == r"C:\Program Files\Google\Chrome\Application\chrome.exe"

            mock_exists.side_effect = exists_side_effect

            command = self.service._build_chrome_command(url, profile)

            self.assertEqual(
                command[0], r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            self.assertIn("--profile-directory=Default", command)
            self.assertEqual(command[-1], url)
