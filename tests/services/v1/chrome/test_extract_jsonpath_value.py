"""
Tests for extract_jsonpath_value utility function.
"""
import os
import json
import tempfile
from unittest.mock import patch
from tests.services.v1.chrome.base import BaseChromeServiceTest
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
