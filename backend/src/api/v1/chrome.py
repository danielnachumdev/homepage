from fastapi import APIRouter, HTTPException
from ...services.v1.chrome_service import ChromeService
from ...schemas.v1.chrome import (
    ChromeProfile, ChromeProfileListResponse, OpenUrlRequest, OpenUrlResponse
)

router = APIRouter(prefix="/chrome", tags=["chrome"])
chrome_service = ChromeService()


@router.get("/profiles", response_model=ChromeProfileListResponse)
async def get_chrome_profiles():
    """Get list of available Chrome profiles from database."""
    response = await chrome_service.load_profiles_from_db()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.get("/profiles/{profile_id}", response_model=ChromeProfile)
async def get_chrome_profile(profile_id: str):
    """Get a specific Chrome profile by ID from database."""
    profile = await chrome_service.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=404, detail=f"Profile not found: {profile_id}")
    return profile


@router.post("/open-url", response_model=OpenUrlResponse)
async def open_url_in_profile(request: OpenUrlRequest):
    """Open a URL in a specific Chrome profile."""
    success = await chrome_service.open_url_in_profile(request.url, request.profile_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to open URL in Chrome profile")

    # Get profile name for response
    profile = await chrome_service.get_profile_by_id(request.profile_id)
    profile_name = profile.name if profile else request.profile_id

    return OpenUrlResponse(
        success=True,
        message=f"Successfully opened {request.url} in profile {profile_name}",
        profile_name=profile_name
    )


# Note: Profile update endpoints removed as ChromeService now only handles discovery and URL opening
# Profile management will be handled through the settings API


__all__ = [
    "router"
]
