from fastapi import APIRouter, HTTPException
from ...services.v1.chrome_service import ChromeService
from ...schemas.v1.chrome import (
    ChromeProfileListResponse, OpenUrlRequest, OpenUrlResponse
)

router = APIRouter(prefix="/chrome", tags=["chrome"])
chrome_service = ChromeService()


@router.get("/profiles", response_model=ChromeProfileListResponse)
async def get_chrome_profiles():
    """Get list of available Chrome profiles."""
    response = await chrome_service.get_chrome_profiles()
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


__all__ = [
    "router"
]
