import os
import json
from typing import Optional, Any
from jsonpath_ng import parse
from ...utils.logger import get_logger
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileListResponse, ChromeProfileInfo
)


def extract_jsonpath_value(data: dict, jsonpath_expr: str) -> Optional[Any]:
    """Extract value from data using jsonpath expression."""
    try:
        jsonpath_expr_parsed = parse(jsonpath_expr)
        matches = [match.value for match in jsonpath_expr_parsed.find(data)]
        return matches[0] if matches else None
    except Exception:
        return None


class ChromeService:
    """Service for discovering and parsing Chrome profiles from the OS."""

    def __init__(self):
        self.logger = get_logger("ChromeService")

    async def discover(self) -> ChromeProfileListResponse:
        """Get list of available Chrome profiles from the system."""
        try:
            # On Windows, Chrome profiles are typically stored in:
            # %LOCALAPPDATA%\Google\Chrome\User Data\
            local_app_data = os.environ.get('LOCALAPPDATA')
            if not local_app_data:
                return ChromeProfileListResponse(
                    success=False,
                    profiles=[],
                    message="Could not determine Chrome profiles location"
                )

            chrome_user_data_path = os.path.join(
                local_app_data, 'Google', 'Chrome', 'User Data')

            if not os.path.exists(chrome_user_data_path):
                return ChromeProfileListResponse(
                    success=False,
                    profiles=[],
                    message="Chrome User Data directory not found"
                )

            profiles = []
            profile_dirs = ["Default"] + [d for d in os.listdir(chrome_user_data_path)
                                          if d.startswith('Profile ') and os.path.isdir(
                    os.path.join(chrome_user_data_path, d))]

            for profile_dir in profile_dirs:
                profile_path = os.path.join(chrome_user_data_path, profile_dir)
                profile_info = self._extract_profile_information(profile_path)

                # Convert to ChromeProfile schema
                chrome_profile = ChromeProfile(
                    id=profile_dir,
                    name=profile_info.profile_name or profile_dir if profile_info else profile_dir,
                    icon=profile_info.picture_url if profile_info else "👤",
                    is_active=False,
                    is_visible=True,
                    path=profile_path
                )

                profiles.append(chrome_profile)
                self.logger.info("Discovered Chrome profile: %s (%s)", chrome_profile.name, profile_dir)

            return ChromeProfileListResponse(
                success=True,
                profiles=profiles,
                message=f"Found {len(profiles)} Chrome profiles"
            )

        except Exception as e:
            self.logger.error("Error getting Chrome profiles: %s", str(e))
            return ChromeProfileListResponse(
                success=False,
                profiles=[],
                message=f"Error getting Chrome profiles: {str(e)}"
            )

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

        except Exception as e:
            self.logger.warning(
                "Error extracting profile information from %s: %s", profile_path, str(e))
            return None


__all__ = [
    "ChromeService"
]
