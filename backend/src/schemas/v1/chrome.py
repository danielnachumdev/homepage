from pydantic import BaseModel
from typing import List, Optional


class ChromeProfile(BaseModel):
    """Chrome profile information."""
    id: str
    name: str
    icon: Optional[str] = None
    is_active: bool = False
    path: Optional[str] = None


class ChromeProfileListResponse(BaseModel):
    """Response containing list of Chrome profiles."""
    success: bool
    profiles: List[ChromeProfile]
    message: Optional[str] = None


class OpenUrlRequest(BaseModel):
    """Request to open a URL in a specific Chrome profile."""
    url: str
    profile_id: str


class OpenUrlResponse(BaseModel):
    """Response for opening URL in Chrome profile."""
    success: bool
    message: str
    profile_name: Optional[str] = None


__all__ = [
    "ChromeProfile",
    "ChromeProfileListResponse", 
    "OpenUrlRequest",
    "OpenUrlResponse"
]
