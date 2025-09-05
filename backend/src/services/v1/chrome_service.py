import os
import json
from typing import Optional, Any

from danielutils.abstractions.db import SelectQuery, WhereClause, Condition, Operator
from jsonpath_ng import parse
from ...utils.logger import get_logger
from ...db.dependencies import get_db
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileListResponse, ChromeProfileInfo
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
        self.db = get_db()

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
                self.logger.info("Discovered Chrome profile: %s (%s)",
                                 chrome_profile.name, profile_dir)

            return ChromeProfileListResponse(
                success=True,
                profiles=profiles,
                message=f"Found {len(profiles)} Chrome profiles"
            )

        except (OSError, FileNotFoundError, PermissionError) as e:
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

        except (OSError, FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError) as e:
            self.logger.warning(
                "Error extracting profile information from %s: %s", profile_path, str(e))
            return None

    async def load_profiles_from_db(self) -> ChromeProfileListResponse:
        """Load Chrome profiles from the database settings table."""
        try:
            self.logger.info("Loading Chrome profiles from database...")

            # Query the settings table for all Chrome profiles
            query = SelectQuery(
                table="settings",
                where=WhereClause(
                    conditions=[
                        Condition(column="category", operator=Operator.EQ,
                                  value="chrome_profiles"),
                        Condition(column="setting_type",
                                  operator=Operator.EQ, value="profile_display")
                    ]
                )
            )

            records = await self.db.get(query)
            profiles = []

            for record in records:
                try:
                    setting_value = json.loads(record["value"])
                    chrome_profile = ChromeProfile(
                        id=setting_value.get("profile_id", ""),
                        name=setting_value.get("display_name", ""),
                        icon=setting_value.get("icon", "👤"),
                        is_active=False,
                        is_visible=setting_value.get("enabled", True),
                        path=""  # Path not stored in settings
                    )
                    profiles.append(chrome_profile)
                    self.logger.info(
                        "Loaded Chrome profile from DB: %s", chrome_profile.name)
                except (json.JSONDecodeError, KeyError) as e:
                    self.logger.warning(
                        "Error parsing profile setting %s: %s", record.get("id", "unknown"), str(e))
                    continue

            return ChromeProfileListResponse(
                success=True,
                profiles=profiles,
                message=f"Loaded {len(profiles)} Chrome profiles from database"
            )

        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            self.logger.error(
                "Error loading Chrome profiles from database: %s", str(e))
            return ChromeProfileListResponse(
                success=False,
                profiles=[],
                message=f"Error loading Chrome profiles from database: {str(e)}"
            )

    async def get_profile_by_id(self, profile_id: str) -> Optional[ChromeProfile]:
        """Get a specific Chrome profile by ID from the database."""
        try:
            from danielutils.abstractions.db import SelectQuery, WhereClause, Condition, Operator

            # Convert profile ID to snake_case for database lookup
            profile_id_snake = profile_id.replace(
                " ", "_").replace("-", "_").lower()
            setting_id = f"chrome_profile_{profile_id_snake}"

            query = SelectQuery(
                table="settings",
                where=WhereClause(
                    conditions=[
                        Condition(column="id", operator=Operator.EQ,
                                  value=setting_id),
                        Condition(column="category",
                                  operator=Operator.EQ, value="chrome_profiles")
                    ]
                )
            )

            records = await self.db.get(query)

            if not records:
                return None

            setting_value = json.loads(records[0]["value"])
            return ChromeProfile(
                id=setting_value.get("profile_id", ""),
                name=setting_value.get("display_name", ""),
                icon=setting_value.get("icon", "👤"),
                is_active=False,
                is_visible=setting_value.get("enabled", True),
                path=""
            )

        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            self.logger.error(
                "Error getting profile %s from database: %s", profile_id, str(e))
            return None

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

            # Get the profile from database
            profile = await self.get_profile_by_id(profile_id)
            if not profile:
                self.logger.error("Profile not found: %s", profile_id)
                return False

            # Build Chrome command
            command = self._build_chrome_command(url, profile)

            # Execute using SystemGateway
            system_gateway = SystemGateway()
            result = await system_gateway.execute_command_args(command)

            if result.success:
                self.logger.info(
                    "Successfully opened URL %s in profile %s", url, profile.name)
                return True
            else:
                self.logger.error(
                    "Failed to open URL %s in profile %s: %s", url, profile.name, result.output)
                return False

        except (OSError, FileNotFoundError, PermissionError, ImportError) as e:
            self.logger.error(
                "Error opening URL %s in profile %s: %s", url, profile_id, str(e))
            return False


__all__ = [
    "ChromeService"
]
