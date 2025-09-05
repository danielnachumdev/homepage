from fastapi import APIRouter, HTTPException

from ...services.v1.settings_service import SettingsService
from ...schemas.v1.settings import (
    SettingsResponse, SettingUpdateRequest, SettingUpdateResponse,
    BulkSettingsUpdateRequest, BulkSettingsUpdateResponse
)

router = APIRouter(prefix="/settings", tags=["settings"])
settings_service = SettingsService()


@router.get("/", response_model=SettingsResponse)
async def get_all_settings():
    """Get all application settings in a unified format."""
    response = await settings_service.get_all_settings()
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


# Convenience endpoints for specific setting types
@router.put("/speed-test")
async def update_speed_test_setting(enabled: bool):
    """Update speed test setting."""
    response = await settings_service.update_speed_test_setting(enabled)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.put("/search-engine")
async def update_search_engine_setting(selected_engine: str):
    """Update search engine setting."""
    response = await settings_service.update_search_engine_setting(selected_engine)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
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