from fastapi import APIRouter, HTTPException
from ...services.v1.chrome_service import ChromeService
from ...schemas.v1.chrome import (
    ChromeProfileListResponse, OpenUrlRequest, OpenUrlResponse,
    UpdateProfileVisibilityRequest, UpdateProfileDisplayRequest, ProfileUpdateResponse,
    UpdateProfileSettingsRequest
)

router = APIRouter(prefix="/chrome", tags=["chrome"])
chrome_service = ChromeService()


@router.get("/profiles", response_model=ChromeProfileListResponse)
async def get_chrome_profiles():
    """Get list of available Chrome profiles."""
    response = await chrome_service.discover()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.post("/open-url", response_model=OpenUrlResponse)
async def open_url_in_profile(request: OpenUrlRequest):
    """Open a URL in a specific Chrome profile."""
    response = await chrome_service.open_url_in_profile(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.put("/profiles/{profile_id}/visibility", response_model=ProfileUpdateResponse)
async def update_profile_visibility(profile_id: str, request: UpdateProfileVisibilityRequest):
    """Update the visibility of a Chrome profile."""
    if request.profile_id != profile_id:
        raise HTTPException(status_code=400, detail="Profile ID mismatch")

    response = await chrome_service.update_profile_visibility(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.put("/profiles/{profile_id}/display", response_model=ProfileUpdateResponse)
async def update_profile_display_info(profile_id: str, request: UpdateProfileDisplayRequest):
    """Update the display information of a Chrome profile."""
    if request.profile_id != profile_id:
        raise HTTPException(status_code=400, detail="Profile ID mismatch")

    response = await chrome_service.update_profile_display_info(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.put("/profiles/{profile_id}/settings", response_model=ProfileUpdateResponse)
async def update_profile_settings(profile_id: str, request: UpdateProfileSettingsRequest):
    """Update the settings of a Chrome profile (icon, enabled, display_name)."""
    if request.profile_id != profile_id:
        raise HTTPException(status_code=400, detail="Profile ID mismatch")

    response = await chrome_service.update_profile_settings(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


__all__ = [
    "router"
]
