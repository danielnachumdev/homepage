from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.src import CommandExecutionResult


class ChromeProfileInfo(BaseModel):
    """Detailed Chrome profile information extracted from Preferences file."""
    profile_name: Optional[str] = None
    account_id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    given_name: Optional[str] = None
    picture_url: Optional[str] = None
    locale: Optional[str] = None


class ChromeProfile(BaseModel):
    """Chrome profile information."""
    id: str
    name: str
    icon: Optional[str] = None
    is_active: bool = False
    is_visible: Optional[bool] = True
    path: Optional[str] = None


class OpenUrlRequest(BaseModel):
    """Request to open a URL in a specific Chrome profile."""
    url: str
    profile_id: str


class OpenUrlResponse(BaseModel):
    """Response for opening URL in Chrome profile."""
    success: bool
    message: str
    profile_name: Optional[str] = None


class UpdateProfileVisibilityRequest(BaseModel):
    """Request to update profile visibility."""
    profile_id: str
    is_visible: bool


class UpdateProfileDisplayRequest(BaseModel):
    """Request to update profile display information."""
    profile_id: str
    display_name: str
    icon: str


class UpdateProfileSettingsRequest(BaseModel):
    """Request to update profile settings (icon, enabled, display_name)."""
    profile_id: str
    display_name: str
    icon: str
    enabled: bool


class ProfileUpdateResponse(BaseModel):
    """Response for profile update operations."""
    success: bool
    message: str


class ChromeOpenRequestResult(BaseModel):
    """Handle for a Chrome process opened by the service."""
    model_config = {"arbitrary_types_allowed": True}

    result: Optional[CommandExecutionResult] = None
    profile_id: str
    url: str


__all__ = [
    "ChromeProfile",
    "ChromeProfileInfo",
    "ChromeOpenRequestResult",
    "OpenUrlRequest",
    "OpenUrlResponse",
    "UpdateProfileVisibilityRequest",
    "UpdateProfileDisplayRequest",
    "UpdateProfileSettingsRequest",
    "ProfileUpdateResponse"
]
