import os
import json
import subprocess
from typing import List, Optional, Any
from jsonpath_ng import parse
from ...gateways.v1.system_gateway import SystemGateway
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileListResponse, OpenUrlRequest, OpenUrlResponse, ChromeProfileInfo
)


class ChromeService:
    """Service for managing Chrome profiles and opening URLs."""

    def __init__(self):
        self.system_gateway = SystemGateway()

    async def get_chrome_profiles(self) -> ChromeProfileListResponse:
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

            # Default profile is always available
            profiles.append(ChromeProfile(
                id="Default",
                name="Default",
                icon="👤",
                is_active=True,
                path=os.path.join(chrome_user_data_path, "Default")
            ))

            # Look for additional profiles
            profile_dirs = [d for d in os.listdir(chrome_user_data_path)
                            if d.startswith('Profile ') and os.path.isdir(os.path.join(chrome_user_data_path, d))]

            for profile_dir in profile_dirs:
                profile_path = os.path.join(chrome_user_data_path, profile_dir)
                profile_info = self._extract_profile_information(profile_path)
                profile_name = profile_info.profile_name if profile_info else None

                profiles.append(ChromeProfile(
                    id=profile_dir,
                    name=profile_name or profile_dir,
                    icon="👤",
                    is_active=False,
                    path=profile_path
                ))

            return ChromeProfileListResponse(
                success=True,
                profiles=profiles,
                message=f"Found {len(profiles)} Chrome profiles"
            )

        except Exception as e:
            return ChromeProfileListResponse(
                success=False,
                profiles=[],
                message=f"Error getting Chrome profiles: {str(e)}"
            )

    async def open_url_in_profile(self, request: OpenUrlRequest) -> OpenUrlResponse:
        """Open a URL in a specific Chrome profile."""
        try:
            # Find the profile by ID
            profiles_response = await self.get_chrome_profiles()
            if not profiles_response.success:
                return OpenUrlResponse(
                    success=False,
                    message="Failed to get Chrome profiles"
                )

            target_profile = None
            for profile in profiles_response.profiles:
                if profile.id == request.profile_id:
                    target_profile = profile
                    break

            if not target_profile:
                return OpenUrlResponse(
                    success=False,
                    message=f"Chrome profile '{request.profile_id}' not found"
                )

            # Build Chrome command with profile
            chrome_command = self._build_chrome_command(
                request.url, target_profile)

            # Execute the command
            result = await self.system_gateway.execute_command_args(chrome_command)

            if result.success:
                return OpenUrlResponse(
                    success=True,
                    message=f"Successfully opened URL in profile '{target_profile.name}'",
                    profile_name=target_profile.name
                )
            else:
                return OpenUrlResponse(
                    success=False,
                    message=f"Failed to open URL: {result.error or 'Unknown error'}"
                )

        except Exception as e:
            return OpenUrlResponse(
                success=False,
                message=f"Error opening URL in profile: {str(e)}"
            )

    async def get_profile_details(self, profile_id: str) -> Optional[ChromeProfileInfo]:
        """Get detailed information for a specific Chrome profile."""
        try:
            # Get all profiles to find the target one
            profiles_response = await self.get_chrome_profiles()
            if not profiles_response.success:
                return None

            # Find the target profile
            target_profile = None
            for profile in profiles_response.profiles:
                if profile.id == profile_id and profile.path:
                    target_profile = profile
                    break

            if not target_profile:
                return None

            # Extract detailed profile information
            return self._extract_profile_information(target_profile.path)

        except Exception:
            return None

    def _extract_profile_information(self, profile_path: str) -> Optional[ChromeProfileInfo]:
        """Extract comprehensive profile information from Chrome profile directory."""
        try:
            preferences_file = os.path.join(profile_path, 'Preferences')
            if not os.path.exists(preferences_file):
                return None

            with open(preferences_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)

                # Use jsonpath for cleaner data extraction
                profile_name = self._extract_jsonpath_value(
                    preferences, '$.profile.name')

                # Extract account information using jsonpath
                account_data = self._extract_jsonpath_value(
                    preferences, '$.account_id_mapping.account_info[0]') or {}

                # Extract relevant account details
                account_id = self._extract_jsonpath_value(
                    account_data, '$.account_id')
                email = self._extract_jsonpath_value(account_data, '$.email')
                full_name = self._extract_jsonpath_value(
                    account_data, '$.full_name')
                given_name = self._extract_jsonpath_value(
                    account_data, '$.given_name')
                picture_url = self._extract_jsonpath_value(
                    account_data, '$.picture_url')
                locale = self._extract_jsonpath_value(account_data, '$.locale')

                return ChromeProfileInfo(
                    profile_name=profile_name,
                    account_id=account_id,
                    email=email,
                    full_name=full_name,
                    given_name=given_name,
                    picture_url=picture_url,
                    locale=locale
                )

        except Exception:
            pass
        return None

    def _extract_jsonpath_value(self, data: dict, jsonpath_expr: str) -> Optional[Any]:
        """Extract value from data using jsonpath expression."""
        try:
            jsonpath_expr_parsed = parse(jsonpath_expr)
            matches = [
                match.value for match in jsonpath_expr_parsed.find(data)]
            return matches[0] if matches else None
        except Exception:
            return None

    def _build_chrome_command(self, url: str, profile: ChromeProfile) -> List[str]:
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


__all__ = [
    "ChromeService"
]
