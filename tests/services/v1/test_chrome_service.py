"""
Tests for ChromeService.
"""
import os
import json
import tempfile
from unittest.mock import patch
from .base_test import BaseChromeServiceTest
from backend.src.services.v1.chrome_service import ChromeService, extract_jsonpath_value
from backend.src.schemas.v1.chrome import ChromeProfile, ChromeProfileInfo


class TestExtractJsonpathValue(BaseChromeServiceTest):
    """Test the extract_jsonpath_value utility function."""

    def test_extract_jsonpath_value_success(self):
        """Test successful extraction of value using jsonpath."""
        data = {
            "profile": {"name": "Test Profile"},
            "account_info": [{"email": "test@example.com"}]
        }

        # Test simple path
        result = extract_jsonpath_value(data, "$.profile.name")
        self.assertEqual(result, "Test Profile")

        # Test array path
        result = extract_jsonpath_value(data, "$.account_info[0].email")
        self.assertEqual(result, "test@example.com")

    def test_extract_jsonpath_value_not_found(self):
        """Test extraction when path doesn't exist."""
        data = {"profile": {"name": "Test Profile"}}

        result = extract_jsonpath_value(data, "$.nonexistent.path")
        self.assertIsNone(result)

    def test_extract_jsonpath_value_invalid_expression(self):
        """Test extraction with invalid jsonpath expression."""
        data = {"profile": {"name": "Test Profile"}}

        result = extract_jsonpath_value(data, "invalid[")
        self.assertIsNone(result)

    def test_extract_jsonpath_value_invalid_data(self):
        """Test extraction with invalid data type."""
        result = extract_jsonpath_value("not a dict", "$.profile.name")
        self.assertIsNone(result)


class TestChromeService(BaseChromeServiceTest):
    """Test the ChromeService class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = ChromeService()

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service.logger)

    def test_extract_profile_information_success(self):
        """Test successful profile information extraction."""
        # Create a temporary directory and preferences file
        with tempfile.TemporaryDirectory() as temp_dir:
            preferences_file = os.path.join(temp_dir, "Preferences")
            preferences_data = {
                "profile": {"name": "Test Profile"},
                "account_info": [{
                    "account_id": "12345",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "given_name": "Test",
                    "picture_url": "https://example.com/pic.jpg",
                    "locale": "en-US"
                }]
            }

            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences_data, f)

            result = self.service._extract_profile_information(temp_dir)

            self.assertIsNotNone(result)
            self.assertIsInstance(result, ChromeProfileInfo)
            self.assertEqual(result.profile_name, "Test Profile")
            self.assertEqual(result.account_id, "12345")
            self.assertEqual(result.email, "test@example.com")
            self.assertEqual(result.full_name, "Test User")
            self.assertEqual(result.given_name, "Test")
            self.assertEqual(result.picture_url, "https://example.com/pic.jpg")
            self.assertEqual(result.locale, "en-US")

    def test_extract_profile_information_no_preferences_file(self):
        """Test profile extraction when Preferences file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.service._extract_profile_information(temp_dir)
            self.assertIsNone(result)

    def test_extract_profile_information_invalid_json(self):
        """Test profile extraction with invalid JSON in Preferences file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            preferences_file = os.path.join(temp_dir, "Preferences")
            with open(preferences_file, 'w', encoding='utf-8') as f:
                f.write("invalid json content")

            result = self.service._extract_profile_information(temp_dir)
            self.assertIsNone(result)

    def test_extract_profile_information_missing_data(self):
        """Test profile extraction with missing account info."""
        with tempfile.TemporaryDirectory() as temp_dir:
            preferences_file = os.path.join(temp_dir, "Preferences")
            preferences_data = {
                "profile": {"name": "Test Profile"}
                # No account_info
            }

            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences_data, f)

            result = self.service._extract_profile_information(temp_dir)

            self.assertIsNotNone(result)
            self.assertEqual(result.profile_name, "Test Profile")
            self.assertIsNone(result.account_id)
            self.assertIsNone(result.email)

    def test_build_chrome_command(self):
        """Test Chrome command building."""
        profile = ChromeProfile(id="Profile 1", name="Test Profile")
        url = "https://example.com"

        command = self.service._build_chrome_command(url, profile)

        self.assertIsInstance(command, list)
        self.assertIn("--profile-directory=Profile 1", command)
        self.assertIn("--new-window", command)
        self.assertIn("--no-first-run", command)
        self.assertIn("--no-default-browser-check", command)
        self.assertEqual(command[-1], url)

    @patch('os.path.exists')
    def test_build_chrome_command_chrome_paths(self, mock_exists):
        """Test Chrome command building with different Chrome paths."""
        # Mock Chrome executable not found in common paths
        mock_exists.return_value = False

        profile = ChromeProfile(id="Profile 1", name="Test Profile")
        url = "https://example.com"

        command = self.service._build_chrome_command(url, profile)

        # Should fall back to chrome.exe in PATH
        self.assertEqual(command[0], "chrome.exe")

    def test_open_url_in_profile_success(self):
        """Test successful URL opening in profile."""
        # Set up mock response
        self.mock_system_gateway.set_mock_response(
            "chrome.exe --profile-directory=test_profile --new-window --no-first-run --no-default-browser-check https://example.com",
            success=True,
            output="Chrome opened successfully"
        )

        result = self.run_async(
            self.service.open_url_in_profile(
                "https://example.com", "test_profile")
        )

        self.assertTrue(result)
        self.assertEqual(len(self.mock_system_gateway.commands_executed), 1)

    def test_open_url_in_profile_failure(self):
        """Test URL opening failure."""
        # Set up mock response for failure
        self.mock_system_gateway.set_mock_response(
            "chrome.exe --profile-directory=test_profile --new-window --no-first-run --no-default-browser-check https://example.com",
            success=False,
            output="Chrome failed to open",
            error="Permission denied"
        )

        result = self.run_async(
            self.service.open_url_in_profile(
                "https://example.com", "test_profile")
        )

        self.assertFalse(result)
        self.assertEqual(len(self.mock_system_gateway.commands_executed), 1)

    def test_open_url_in_profile_exception(self):
        """Test URL opening with exception."""
        # Make the mock raise an exception
        self.mock_system_gateway_class.side_effect = ImportError(
            "SystemGateway not available")

        result = self.run_async(
            self.service.open_url_in_profile(
                "https://example.com", "test_profile")
        )

        self.assertFalse(result)


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
