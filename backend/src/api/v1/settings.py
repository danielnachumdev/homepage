from fastapi import APIRouter, HTTPException

from ...services.v1.settings_service import SettingsService
from ...schemas.v1.settings import (
    SettingsResponse, SettingUpdateRequest, SettingUpdateResponse,
    BulkSettingsUpdateRequest, BulkSettingsUpdateResponse,
    ChromeProfileSettingsResponse, SearchEngineSettingsResponse,
    SpeedTestSettingsResponse
)

router = APIRouter(prefix="/settings", tags=["settings"])
settings_service = SettingsService()


@router.get("/", response_model=SettingsResponse)
async def get_all_settings():
    """Get all application settings."""
    response = await settings_service.get_all_settings()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.get("/category/{category}", response_model=SettingsResponse)
async def get_settings_by_category(category: str):
    """Get settings for a specific category."""
    response = await settings_service.get_settings_by_category(category)
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.put("/update", response_model=SettingUpdateResponse)
async def update_setting(request: SettingUpdateRequest):
    """Update a specific setting."""
    response = await settings_service.update_setting(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.put("/bulk-update", response_model=BulkSettingsUpdateResponse)
async def bulk_update_settings(request: BulkSettingsUpdateRequest):
    """Update multiple settings at once."""
    response = await settings_service.bulk_update_settings(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


# Chrome Profile specific endpoints
@router.get("/chrome-profiles", response_model=ChromeProfileSettingsResponse)
async def get_chrome_profile_settings():
    """Get Chrome profile settings."""
    response = await settings_service.get_chrome_profile_settings()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.put("/chrome-profiles/{profile_id}")
async def update_chrome_profile_setting(
    profile_id: str,
    display_name: str,
    icon: str,
    enabled: bool
):
    """Update Chrome profile setting."""
    response = await settings_service.update_chrome_profile_setting(
        profile_id, display_name, icon, enabled
    )
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


# Search Engine specific endpoints
@router.get("/search-engine", response_model=SearchEngineSettingsResponse)
async def get_search_engine_setting():
    """Get search engine setting."""
    response = await settings_service.get_search_engine_setting()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.put("/search-engine")
async def update_search_engine_setting(selected_engine: str):
    """Update search engine setting."""
    response = await settings_service.update_search_engine_setting(selected_engine)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


# Speed Test specific endpoints
@router.get("/speed-test", response_model=SpeedTestSettingsResponse)
async def get_speed_test_setting():
    """Get speed test setting."""
    response = await settings_service.get_speed_test_setting()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.put("/speed-test")
async def update_speed_test_setting(enabled: bool):
    """Update speed test setting."""
    response = await settings_service.update_speed_test_setting(enabled)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


__all__ = [
    "router"
]
