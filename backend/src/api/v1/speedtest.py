from fastapi import APIRouter, HTTPException
from ...services.v1.speedtest_service import SpeedTestService
from ...schemas.v1.speedtest import (
    SpeedTestRequest, SpeedTestResponse, SpeedTestConfigResponse
)

router = APIRouter(prefix="/speedtest", tags=["speedtest"])
speedtest_service = SpeedTestService()


@router.post("/test", response_model=SpeedTestResponse)
async def perform_speed_test(request: SpeedTestRequest):
    """Perform a single speed test."""
    response = await speedtest_service.perform_speed_test(request)
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.post("/start", response_model=SpeedTestConfigResponse)
async def start_continuous_testing(request: SpeedTestRequest):
    """Start continuous speed testing with specified interval."""
    response = await speedtest_service.start_continuous_testing(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.post("/stop", response_model=SpeedTestConfigResponse)
async def stop_continuous_testing():
    """Stop continuous speed testing."""
    response = await speedtest_service.stop_continuous_testing()
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.get("/config", response_model=SpeedTestConfigResponse)
async def get_config():
    """Get current speed test configuration."""
    response = await speedtest_service.get_current_config()
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)
    return response


@router.get("/result", response_model=SpeedTestResponse)
async def get_last_result():
    """Get the last speed test result."""
    response = await speedtest_service.get_last_result()
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response


@router.get("/status")
async def get_status():
    """Get speed test service status."""
    config_response = await speedtest_service.get_current_config()
    result_response = await speedtest_service.get_last_result()

    return {
        "is_running": config_response.config.get("is_running", False) if config_response.config else False,
        "interval_seconds": config_response.config.get("interval_seconds", 1) if config_response.config else 1,
        "has_result": result_response.success,
        "last_test_time": result_response.result.timestamp.isoformat() if result_response.result else None
    }


@router.get("/partial-result")
async def get_partial_result():
    """Get the latest partial speed test result."""
    response = await speedtest_service.get_last_result()
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response


__all__ = [
    "router"
]
