from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class SettingValue(BaseModel):
    """A single setting value."""
    id: str = Field(..., description="Setting identifier")
    category: str = Field(..., description="Setting category")
    setting_type: str = Field(..., description="Type of setting")
    value: Any = Field(..., description="Setting value")
    description: Optional[str] = Field(
        None, description="Human-readable description")
    is_user_editable: bool = Field(
        True, description="Whether user can edit this setting")
    created_at: Optional[datetime] = Field(
        None, description="When setting was created")
    updated_at: Optional[datetime] = Field(
        None, description="When setting was last updated")


class SettingsResponse(BaseModel):
    """Response containing settings."""
    success: bool
    settings: List[SettingValue]
    message: Optional[str] = None


class SettingUpdateRequest(BaseModel):
    """Request to update a setting."""
    id: str = Field(..., description="Setting identifier")
    value: Any = Field(..., description="New setting value")


class SettingUpdateResponse(BaseModel):
    """Response for setting update."""
    success: bool
    message: str
    setting: Optional[SettingValue] = None


class SettingsByCategoryResponse(BaseModel):
    """Response containing settings grouped by category."""
    success: bool
    settings: Dict[str, List[SettingValue]]
    message: Optional[str] = None


class BulkSettingsUpdateRequest(BaseModel):
    """Request to update multiple settings at once."""
    settings: List[SettingUpdateRequest] = Field(
        ..., description="List of settings to update")


class BulkSettingsUpdateResponse(BaseModel):
    """Response for bulk settings update."""
    success: bool
    updated_settings: List[SettingValue]
    failed_updates: List[Dict[str, Any]]
    message: Optional[str] = None


# Chrome Profile specific settings
class ChromeProfileSettingValue(BaseModel):
    """Chrome profile setting value."""
    profile_id: str
    display_name: str
    icon: str
    enabled: bool


class ChromeProfileSettingsResponse(BaseModel):
    """Response containing Chrome profile settings."""
    success: bool
    profiles: List[ChromeProfileSettingValue]
    message: Optional[str] = None


# Search Engine specific settings
class SearchEngineSettingValue(BaseModel):
    """Search engine setting value."""
    selected_engine: str


class SearchEngineSettingsResponse(BaseModel):
    """Response containing search engine settings."""
    success: bool
    setting: SearchEngineSettingValue
    message: Optional[str] = None


# Speed Test specific settings
class SpeedTestSettingValue(BaseModel):
    """Speed test setting value."""
    enabled: bool


class SpeedTestSettingsResponse(BaseModel):
    """Response containing speed test settings."""
    success: bool
    setting: SpeedTestSettingValue
    message: Optional[str] = None


__all__ = [
    "SettingValue",
    "SettingsResponse",
    "SettingUpdateRequest",
    "SettingUpdateResponse",
    "SettingsByCategoryResponse",
    "BulkSettingsUpdateRequest",
    "BulkSettingsUpdateResponse",
    "ChromeProfileSettingValue",
    "ChromeProfileSettingsResponse",
    "SearchEngineSettingValue",
    "SearchEngineSettingsResponse",
    "SpeedTestSettingValue",
    "SpeedTestSettingsResponse"
]
