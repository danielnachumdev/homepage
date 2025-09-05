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
    """Generic response containing all application settings."""
    success: bool
    message: Optional[str] = None
    settings: List[SettingValue] = Field(...,
                                         description="All settings from database")


class SettingUpdateRequest(BaseModel):
    """Request to update a setting."""
    id: str = Field(..., description="Setting identifier")
    value: Any = Field(..., description="New setting value")


class SettingUpdateResponse(BaseModel):
    """Response for setting update."""
    success: bool
    message: str
    setting: Optional[SettingValue] = None


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


__all__ = [
    "SettingValue",
    "SettingsResponse",
    "SettingUpdateRequest",
    "SettingUpdateResponse",
    "BulkSettingsUpdateRequest",
    "BulkSettingsUpdateResponse"
]
