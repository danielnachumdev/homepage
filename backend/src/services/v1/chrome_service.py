import os
import json
import subprocess
from typing import List, Optional, Any
from jsonpath_ng import parse
from ...gateways.v1.system_gateway import SystemGateway
from ...db.dependencies import get_db
from ...db.models.chrome_profile import ChromeProfileModel
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileListResponse, OpenUrlRequest, OpenUrlResponse, ChromeProfileInfo,
    UpdateProfileVisibilityRequest, UpdateProfileDisplayRequest, ProfileUpdateResponse
)


class ChromeService:
    """Service for managing Chrome profiles and opening URLs."""

    def __init__(self):
        self.system_gateway = SystemGateway()
        self.db = get_db()

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
            default_path = os.path.join(chrome_user_data_path, "Default")
            default_profile_info = self._extract_profile_information(
                default_path)

            # Get or create profile in database
            default_db_profile = await self.get_or_create_profile(
                "Default", "Default", default_path, default_profile_info
            )

            profiles.append(
                self.convert_to_schema(default_db_profile))

            # Look for additional profiles
            profile_dirs = [d for d in os.listdir(chrome_user_data_path)
                            if d.startswith('Profile ') and os.path.isdir(os.path.join(chrome_user_data_path, d))]

            for profile_dir in profile_dirs:
                profile_path = os.path.join(chrome_user_data_path, profile_dir)
                profile_info = self._extract_profile_information(profile_path)
                profile_name = profile_info.profile_name if profile_info else None

                # Get or create profile in database
                db_profile = await self.get_or_create_profile(
                    profile_dir, profile_name or profile_dir, profile_path, profile_info
                )

                profiles.append(
                    self.convert_to_schema(db_profile))

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

    async def get_or_create_profile(self, profile_id: str, name: str, path: str,
                                    profile_info: Optional[ChromeProfileInfo] = None) -> ChromeProfileModel:
        """Get existing profile or create new one if it doesn't exist."""
        try:
            # Try to get existing profile
            existing_profile = await self.get_profile(profile_id)
            if existing_profile:
                return existing_profile

            # Create new profile
            new_profile = ChromeProfileModel(
                id=profile_id,
                name=name,
                display_name=name,  # Default to system name
                icon="👤",  # Default icon
                is_active=False,
                is_visible=True,
                path=path,
                profile_name=profile_info.profile_name if profile_info else None,
                account_id=profile_info.account_id if profile_info else None,
                email=profile_info.email if profile_info else None,
                full_name=profile_info.full_name if profile_info else None,
                given_name=profile_info.given_name if profile_info else None,
                picture_url=profile_info.picture_url if profile_info else None,
                locale=profile_info.locale if profile_info else None
            )

            # Save to database
            await self.save_profile(new_profile)
            return new_profile

        except Exception as e:
            print(f"Error in get_or_create_profile: {e}")
            # Return a basic profile if database fails
            return ChromeProfileModel(
                id=profile_id,
                name=name,
                display_name=name,
                icon="👤",
                is_active=False,
                is_visible=True,
                path=path
            )

    async def get_profile(self, profile_id: str) -> Optional[ChromeProfileModel]:
        """Get a Chrome profile by ID from the database."""
        try:
            # This would need to be implemented based on the specific database backend
            # For now, we'll use a placeholder approach
            return None
        except Exception as e:
            print(f"Error getting profile {profile_id}: {e}")
            return None

    async def save_profile(self, profile: ChromeProfileModel) -> bool:
        """Save a Chrome profile to the database."""
        try:
            # This would need to be implemented based on the specific database backend
            # For now, we'll use a placeholder approach
            return True
        except Exception as e:
            print(f"Error saving profile {profile.id}: {e}")
            return False

    def convert_to_schema(self, model: ChromeProfileModel) -> ChromeProfile:
        """Convert database model to API schema."""
        return ChromeProfile(
            id=model.id,
            name=model.display_name or model.name,
            icon=model.icon,
            is_active=model.is_active,
            path=model.path
        )

    async def update_profile_visibility(self, request: UpdateProfileVisibilityRequest) -> ProfileUpdateResponse:
        """Update the visibility of a Chrome profile."""
        try:
            profile = await self.get_profile(request.profile_id)
            if profile:
                profile.is_visible = request.is_visible
                success = await self.save_profile(profile)

                if success:
                    return ProfileUpdateResponse(
                        success=True,
                        message=f"Profile visibility updated successfully"
                    )
                else:
                    return ProfileUpdateResponse(
                        success=False,
                        message="Failed to update profile visibility"
                    )
            else:
                return ProfileUpdateResponse(
                    success=False,
                    message="Profile not found"
                )

        except Exception as e:
            return ProfileUpdateResponse(
                success=False,
                message=f"Error updating profile visibility: {str(e)}"
            )

    async def update_profile_display_info(self, request: UpdateProfileDisplayRequest) -> ProfileUpdateResponse:
        """Update the display information of a Chrome profile."""
        try:
            profile = await self.get_profile(request.profile_id)
            if profile:
                profile.display_name = request.display_name
                profile.icon = request.icon
                success = await self.save_profile(profile)

                if success:
                    return ProfileUpdateResponse(
                        success=True,
                        message=f"Profile display information updated successfully"
                    )
                else:
                    return ProfileUpdateResponse(
                        success=False,
                        message="Failed to update profile display information"
                    )
            else:
                return ProfileUpdateResponse(
                    success=False,
                    message="Profile not found"
                )

        except Exception as e:
            return ProfileUpdateResponse(
                success=False,
                message=f"Error updating profile display information: {str(e)}"
            )

    async def get_all_visible_profiles(self) -> List[ChromeProfileModel]:
        """Get all visible Chrome profiles from the database."""
        try:
            # This would need to be implemented based on the specific database backend
            # For now, we'll use a placeholder approach that returns empty list
            # In a real implementation, this would query the database for visible profiles
            return []
        except Exception as e:
            print(f"Error getting visible profiles: {e}")
            return []


__all__ = [
    "ChromeService"
]
