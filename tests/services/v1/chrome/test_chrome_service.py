"""
Tests for ChromeService class.
"""
import os
import json
import tempfile
from unittest.mock import patch
from tests.services.v1.chrome.base import BaseChromeServiceTest
from backend.src.services.v1.chrome_service import ChromeService
from backend.src.schemas.v1.chrome import ChromeProfile, ChromeProfileInfo


class TestChromeService(BaseChromeServiceTest):
    """Test the ChromeService class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.service = ChromeService()

    def test_init(self):
        """Test service initialization."""
        self.logger.info("Testing ChromeService initialization")
        self.assertIsNotNone(self.service.logger)
        self.logger.info("ChromeService initialization test completed successfully")

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
        self.run_async(self.service.open_url_in_profile("https://example.com", "test_profile"))

    def test_open_url_in_profile_invalid_url(self):
        """Test URL opening with invalid URL."""
        # Test with an invalid URL - should raise ValueError
        with self.assertRaises(ValueError):
            self.run_async(self.service.open_url_in_profile("invalid-url", "test_profile"))

    def test_open_url_in_profile_empty_url(self):
        """Test URL opening with empty URL."""
        # Test with empty URL - should raise ValueError
        with self.assertRaises(ValueError):
            self.run_async(self.service.open_url_in_profile("", "test_profile"))

    def test_open_url_in_profile_none_url(self):
        """Test URL opening with None URL."""
        # Test with None URL - should raise ValueError
        with self.assertRaises(ValueError):
            self.run_async(self.service.open_url_in_profile(None, "test_profile"))

    def test_open_url_in_profile_invalid_profile_id(self):
        """Test URL opening with invalid profile ID."""
        # Test with empty profile ID - should raise ValueError
        with self.assertRaises(ValueError):
            self.run_async(self.service.open_url_in_profile("https://example.com", ""))

    def test_open_url_in_profile_unsupported_scheme(self):
        """Test URL opening with unsupported scheme."""
        # Test with unsupported scheme - should raise ValueError
        with self.assertRaises(ValueError):
            self.run_async(self.service.open_url_in_profile("ftp://example.com", "test_profile"))

    def test_open_url_in_profile_url_normalization(self):
        """Test URL normalization (adding https:// prefix)."""
        # Test that URLs without scheme get https:// prefix added
        self.run_async(self.service.open_url_in_profile("example.com", "test_profile"))

    def test_validate_and_normalize_url_valid_urls(self):
        """Test URL validation and normalization with valid URLs."""
        self.logger.info("Testing URL validation and normalization with valid URLs")

        # Test with https URL
        result = self.service._validate_and_normalize_url("https://example.com")
        self.assertEqual(result, "https://example.com")
        self.logger.info("HTTPS URL validation passed")

        # Test with http URL
        result = self.service._validate_and_normalize_url("http://example.com")
        self.assertEqual(result, "http://example.com")

        # Test with www URL (should add https://)
        result = self.service._validate_and_normalize_url("www.example.com")
        self.assertEqual(result, "https://www.example.com")

        # Test with domain only (should add https://)
        result = self.service._validate_and_normalize_url("example.com")
        self.assertEqual(result, "https://example.com")

        # Test with file URL
        result = self.service._validate_and_normalize_url(
            "file:///path/to/file")
        self.assertEqual(result, "file:///path/to/file")

    def test_validate_and_normalize_url_invalid_urls(self):
        """Test URL validation with invalid URLs."""
        # Test with empty string
        with self.assertRaises(ValueError, msg="URL must be a non-empty string"):
            self.service._validate_and_normalize_url("")

        # Test with None
        with self.assertRaises(ValueError, msg="URL must be a non-empty string"):
            self.service._validate_and_normalize_url(None)

        # Test with non-string
        with self.assertRaises(ValueError, msg="URL must be a non-empty string"):
            self.service._validate_and_normalize_url(123)

        # Test with unsupported scheme
        with self.assertRaises(ValueError, msg="Unsupported URL scheme"):
            self.service._validate_and_normalize_url("ftp://example.com")

        # Test with invalid format
        with self.assertRaises(ValueError, msg="Invalid URL format"):
            self.service._validate_and_normalize_url("://example.com")

    def test_validate_profile_id_valid(self):
        """Test profile ID validation with valid IDs."""
        # Should not raise any exception
        self.service._validate_profile_id("test_profile")
        self.service._validate_profile_id("Profile 1")
        self.service._validate_profile_id("default")

    def test_validate_profile_id_invalid(self):
        """Test profile ID validation with invalid IDs."""
        # Test with empty string
        with self.assertRaises(ValueError, msg="Profile ID must be a non-empty string"):
            self.service._validate_profile_id("")

        # Test with None
        with self.assertRaises(ValueError, msg="Profile ID must be a non-empty string"):
            self.service._validate_profile_id(None)

        # Test with non-string
        with self.assertRaises(ValueError, msg="Profile ID must be a non-empty string"):
            self.service._validate_profile_id(123)
