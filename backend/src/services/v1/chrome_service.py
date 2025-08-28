import os
import json
import subprocess
from typing import List, Optional
from ...gateways.v1.system_gateway import SystemGateway
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileListResponse, OpenUrlRequest, OpenUrlResponse
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
                profile_name = self._get_profile_name(profile_path)

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
            chrome_command = self._build_chrome_command(request.url, target_profile)

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

    def _get_profile_name(self, profile_path: str) -> Optional[str]:
        """Extract profile name from Chrome profile directory."""
        try:
            preferences_file = os.path.join(profile_path, 'Preferences')
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    profile_info = preferences.get('profile', {})
                    return profile_info.get('name', '')
        except Exception:
            pass
        return None

    def _build_chrome_command(self, url: str, profile: ChromeProfile) -> List[str]:
        """Build Chrome command with profile specification."""
        # Try to find Chrome executable in common Windows locations
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
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
