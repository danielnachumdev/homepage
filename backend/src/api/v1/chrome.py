from fastapi import APIRouter, HTTPException
from ...services.v1.chrome_service import ChromeService
from ...schemas.v1.chrome import (
    OpenUrlRequest, OpenUrlResponse
)

router = APIRouter(prefix="/chrome", tags=["chrome"])
chrome_service = ChromeService()


# Chrome profile endpoints removed - all profile data is now managed through settings API


@router.post("/open-url", response_model=OpenUrlResponse)
async def open_url_in_profile(request: OpenUrlRequest):
    """Open a URL in a specific Chrome profile."""
    success = await chrome_service.open_url_in_profile(request.url, request.profile_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to open URL in Chrome profile")

    return OpenUrlResponse(
        success=True,
        message=f"Successfully opened {request.url} in profile {request.profile_id}",
        profile_name=request.profile_id
    )


# Note: Profile update endpoints removed as ChromeService now only handles discovery and URL opening
# Profile management will be handled through the settings API


__all__ = [
    "router"
]
