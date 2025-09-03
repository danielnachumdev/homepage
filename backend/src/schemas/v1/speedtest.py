from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SpeedTestRequest(BaseModel):
    """Request to perform a speed test."""
    interval_seconds: Optional[int] = Field(
        default=1, ge=1, le=300, description="Interval between tests in seconds")


class SpeedTestResult(BaseModel):
    """Individual speed test result."""
    download_speed_mbps: Optional[float] = Field(
        default=None, description="Download speed in Mbps")
    upload_speed_mbps: Optional[float] = Field(
        default=None, description="Upload speed in Mbps")
    ping_ms: Optional[float] = Field(
        default=None, description="Ping latency in milliseconds")
    timestamp: Optional[datetime] = Field(
        default=None, description="When the test was performed")
    server_name: Optional[str] = Field(
        default=None, description="Name of the test server")
    server_sponsor: Optional[str] = Field(
        default=None, description="Sponsor of the test server")
    is_download_complete: bool = Field(
        default=False, description="Whether download test is complete")
    is_upload_complete: bool = Field(
        default=False, description="Whether upload test is complete")
    is_ping_complete: bool = Field(
        default=False, description="Whether ping test is complete")


class SpeedTestResponse(BaseModel):
    """Response containing speed test results."""
    success: bool
    result: Optional[SpeedTestResult] = None
    message: Optional[str] = None


class SpeedTestConfigRequest(BaseModel):
    """Request to configure speed test settings."""
    interval_seconds: int = Field(
        ge=1, le=300, description="Interval between tests in seconds")
    auto_start: bool = Field(
        default=True, description="Whether to automatically start testing")


class SpeedTestConfigResponse(BaseModel):
    """Response for speed test configuration."""
    success: bool
    message: str
    config: Optional[dict] = None


__all__ = [
    "SpeedTestRequest",
    "SpeedTestResult",
    "SpeedTestResponse",
    "SpeedTestConfigRequest",
    "SpeedTestConfigResponse"
]
