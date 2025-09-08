import os
import json
from typing import Optional, Any
from urllib.parse import urlparse
from datetime import datetime

# Removed database imports - no longer needed since profiles are managed through settings API
from jsonpath_ng import parse
from ...utils.logger import get_logger
# Removed get_db import - no longer needed since profiles are managed through settings API
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileInfo, ChromeProcessHandle
)
from ...schemas.v1.system import CommandResult


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
        self._opened_processes = []  # Track opened Chrome processes for cleanup

    # Removed discover method - profiles are now managed through settings API

    def _extract_profile_information(self, profile_path: str) -> Optional[ChromeProfileInfo]:
        """Extract profile information from Chrome's Preferences file."""
        self.logger.debug("Starting to extract profile information from: %s", profile_path)
        try:
            preferences_file = os.path.join(profile_path, "Preferences")
            if not os.path.exists(preferences_file):
                self.logger.warning("Preferences file not found at: %s", preferences_file)
                return None

            self.logger.debug("Reading preferences file: %s", preferences_file)
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

            self.logger.debug("Successfully extracted profile information: name=%s, email=%s",
                              profile_name, email)

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
        self.logger.debug("Building Chrome command for URL: %s, profile: %s", url, profile.id)

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
                self.logger.debug("Found Chrome executable at: %s", path)
                break
        if not chrome_exe:
            chrome_exe = "chrome.exe"  # Use PATH as last resort
            self.logger.debug("Using Chrome from PATH: %s", chrome_exe)

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
        self.logger.debug("Built Chrome command: %s", " ".join(args))

        return args

    def _validate_and_normalize_url(self, url: str) -> str:
        """Validate and normalize a URL for Chrome."""

        self.logger.debug("Validating and normalizing URL: %s", url)

        # Validate URL format
        if not url or not isinstance(url, str):
            self.logger.error("Invalid URL: must be a non-empty string")
            raise ValueError("URL must be a non-empty string")

        # Parse the URL to validate its format
        parsed_url = urlparse(url)

        # Check if URL has a scheme (http, https, file, etc.)
        if not parsed_url.scheme:
            # If no scheme, assume it's a web URL and add https://
            if url.startswith(('www.', 'http://', 'https://')):
                self.logger.error("Invalid URL format: %s", url)
                raise ValueError(f"Invalid URL format: {url}")
            else:
                url = f"https://{url}"
                parsed_url = urlparse(url)
                self.logger.debug("Added https:// scheme to URL: %s", url)

        # Validate that the scheme is supported by Chrome
        if parsed_url.scheme not in ('http', 'https', 'file', 'chrome', 'chrome-extension', 'data', 'about'):
            self.logger.error("Unsupported URL scheme: %s", parsed_url.scheme)
            raise ValueError(
                f"Unsupported URL scheme: {parsed_url.scheme}. Supported schemes: http, https, file, chrome, chrome-extension, data, about")

        # Check if URL has a netloc (network location) for http/https URLs
        if parsed_url.scheme in ('http', 'https') and not parsed_url.netloc:
            self.logger.error("Invalid URL: missing domain for %s URL", parsed_url.scheme)
            raise ValueError(f"Invalid URL: missing domain for {parsed_url.scheme} URL")

        self.logger.debug("Successfully validated and normalized URL: %s", url)
        return url

    def _validate_profile_id(self, profile_id: str) -> None:
        """Validate profile ID."""
        self.logger.debug("Validating profile ID: %s", profile_id)
        if not profile_id or not isinstance(profile_id, str):
            self.logger.error("Invalid profile ID: must be a non-empty string")
            raise ValueError("Profile ID must be a non-empty string")
        self.logger.debug("Profile ID validation successful")

    async def open_url_in_profile(self, url: str, profile_id: str) -> ChromeProcessHandle:
        """Open a URL in a specific Chrome profile using SystemGateway."""
        from ...gateways.v1.system_gateway import SystemGateway

        self.logger.info("Starting to open URL in Chrome profile: URL=%s, profile=%s", url, profile_id)

        try:
            # Validate inputs
            self.logger.debug("Validating inputs")
            normalized_url = self._validate_and_normalize_url(url)
            self._validate_profile_id(profile_id)

            # Create a simple profile object with just the id for the existing method
            profile = ChromeProfile(id=profile_id, name=profile_id)

            # Build Chrome command using existing method
            self.logger.debug("Building Chrome command")
            command = self._build_chrome_command(normalized_url, profile)
            command_str = " ".join(command)

            # Execute using SystemGateway
            self.logger.debug("Executing Chrome command via SystemGateway")
            system_gateway = SystemGateway()
            result = await system_gateway.execute_command_args(command)

            if result.success:
                self.logger.info("Successfully opened URL %s in profile %s", normalized_url, profile_id)

                # Create process handle using CommandResult from SystemGateway
                process_handle = ChromeProcessHandle(
                    command_handle=result.result.dict() if result.result else None,
                    profile_id=profile_id,
                    url=normalized_url,
                    is_running=True
                )

                # Track the process for cleanup
                self._opened_processes.append(process_handle)
                self.logger.debug("Created process handle with command handle: %s", result.handle)

                return process_handle
            else:
                self.logger.error("Failed to open URL %s in profile %s: %s", normalized_url, profile_id, result.output)
                raise RuntimeError(f"Failed to open URL: {result.output}")
        except Exception as e:
            self.logger.error("Error opening URL %s in profile %s: %s", url, profile_id, str(e))
            raise

    async def close_chrome_process(self, process_handle: ChromeProcessHandle) -> bool:
        """Close a Chrome process using its handle."""
        pid = process_handle.command_handle.get('pid') if process_handle.command_handle else None
        self.logger.info("Closing Chrome process: PID=%s, profile=%s", pid, process_handle.profile_id)

        try:
            if not process_handle.is_running:
                self.logger.warning("Process is already marked as not running: PID=%s", pid)
                return True

            if pid:
                # Try to terminate the process by PID
                from ...gateways.v1.system_gateway import SystemGateway
                system_gateway = SystemGateway()

                # Use taskkill on Windows to terminate the process
                command = f"taskkill /PID {pid} /F"
                result = await system_gateway.execute_command(command)

                if result.success:
                    process_handle.is_running = False
                    self.logger.info("Successfully closed Chrome process: PID=%s", pid)
                    return True
                else:
                    self.logger.error(
                        "Failed to close Chrome process: PID=%s, error=%s",
                        pid,
                        result.error)
                    return False
            else:
                self.logger.warning("No PID available for process handle")
                return False

        except Exception as e:
            self.logger.error("Error closing Chrome process PID=%s: %s", pid, str(e))
            return False

    async def close_all_chrome_processes(self) -> int:
        """Close all tracked Chrome processes."""
        self.logger.info("Closing all tracked Chrome processes: %d processes", len(self._opened_processes))

        closed_count = 0
        for process_handle in self._opened_processes[:]:  # Copy list to avoid modification during iteration
            if await self.close_chrome_process(process_handle):
                closed_count += 1
                self._opened_processes.remove(process_handle)

        self.logger.info("Closed %d out of %d Chrome processes", closed_count,
                         len(self._opened_processes) + closed_count)
        return closed_count

    def get_opened_processes(self) -> list[ChromeProcessHandle]:
        """Get list of all currently tracked Chrome processes."""
        return self._opened_processes.copy()

    def get_process_by_pid(self, pid: int) -> Optional[ChromeProcessHandle]:
        """Get a Chrome process handle by PID."""
        for process_handle in self._opened_processes:
            handle_pid = process_handle.command_handle.get('pid') if process_handle.command_handle else None
            if handle_pid == pid:
                return process_handle
        return None


__all__ = [
    "ChromeService"
]
