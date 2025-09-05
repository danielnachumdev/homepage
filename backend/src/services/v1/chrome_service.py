import os
import json
from typing import Optional, Any

# Removed database imports - no longer needed since profiles are managed through settings API
from jsonpath_ng import parse
from ...utils.logger import get_logger
# Removed get_db import - no longer needed since profiles are managed through settings API
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileInfo
)


def extract_jsonpath_value(data: dict, jsonpath_expr: str) -> Optional[Any]:
    """Extract value from data using jsonpath expression."""
    try:
        jsonpath_expr_parsed = parse(jsonpath_expr)
        matches = [match.value for match in jsonpath_expr_parsed.find(data)]
        return matches[0] if matches else None
    except (ValueError, TypeError, AttributeError):
        return None


class ChromeService:
    """Service for discovering and parsing Chrome profiles from the OS."""

    def __init__(self):
        self.logger = get_logger("ChromeService")

    # Removed discover method - profiles are now managed through settings API

    def _extract_profile_information(self, profile_path: str) -> Optional[ChromeProfileInfo]:
        """Extract profile information from Chrome's Preferences file."""
        try:
            preferences_file = os.path.join(profile_path, "Preferences")
            if not os.path.exists(preferences_file):
                return None

            with open(preferences_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)

            # Use jsonpath for cleaner data extraction
            profile_name = extract_jsonpath_value(
                preferences, '$.profile.name')

            # Extract account information using jsonpath
            account_data = extract_jsonpath_value(
                preferences, '$.account_info[0]') or {}

            # Extract relevant account details
            account_id = extract_jsonpath_value(account_data, '$.account_id')
            email = extract_jsonpath_value(account_data, '$.email')
            full_name = extract_jsonpath_value(account_data, '$.full_name')
            given_name = extract_jsonpath_value(account_data, '$.given_name')
            picture_url = extract_jsonpath_value(account_data, '$.picture_url')
            locale = extract_jsonpath_value(account_data, '$.locale')

            return ChromeProfileInfo(
                profile_name=profile_name,
                account_id=account_id,
                email=email,
                full_name=full_name,
                given_name=given_name,
                picture_url=picture_url,
                locale=locale
            )

        except (OSError, FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError) as e:
            self.logger.warning(
                "Error extracting profile information from %s: %s", profile_path, str(e))
            return None

    # Removed load_profiles_from_db method - profiles are now managed through settings API

    # Removed get_profile_by_id method - profiles are now managed through settings API

    def _build_chrome_command(self, url: str, profile: ChromeProfile) -> list[str]:
        """Build Chrome command with profile specification."""
        # Try to find Chrome executable in common Windows locations
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get('LOCALAPPDATA', ''),
                         'Google', 'Chrome', 'Application', 'chrome.exe'),
            "chrome.exe"  # Fallback to PATH
        ]

        chrome_exe = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_exe = path
                break
        if not chrome_exe:
            chrome_exe = "chrome.exe"  # Use PATH as last resort

        # Profile directory argument
        profile_arg = f"--profile-directory={profile.id}"

        # Additional arguments for better user experience
        additional_args = [
            "--new-window",  # Open in new window
            "--no-first-run",  # Skip first run setup
            "--no-default-browser-check"  # Skip default browser check
        ]

        # Build the complete command
        args = [chrome_exe, profile_arg] + additional_args + [url]

        return args

    async def open_url_in_profile(self, url: str, profile_id: str) -> bool:
        """Open a URL in a specific Chrome profile using SystemGateway."""
        try:
            from ...gateways.v1.system_gateway import SystemGateway

            # Create a simple profile object with just the id for the existing method
            profile = ChromeProfile(id=profile_id, name=profile_id)

            # Build Chrome command using existing method
            command = self._build_chrome_command(url, profile)

            # Execute using SystemGateway
            system_gateway = SystemGateway()
            result = await system_gateway.execute_command_args(command)

            if result.success:
                self.logger.info(
                    "Successfully opened URL %s in profile %s", url, profile_id)
                return True
            else:
                self.logger.error(
                    "Failed to open URL %s in profile %s: %s", url, profile_id, result.output)
                return False

        except (OSError, FileNotFoundError, PermissionError, ImportError) as e:
            self.logger.error(
                "Error opening URL %s in profile %s: %s", url, profile_id, str(e))
            return False


__all__ = [
    "ChromeService"
]
