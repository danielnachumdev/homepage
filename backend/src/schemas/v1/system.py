from pydantic import BaseModel
from typing import Optional


class CommandRequest(BaseModel):
    command: str


class CommandHandle(BaseModel):
    """Generic handle for a command process executed by SystemGateway."""
    pid: Optional[int] = None
    command: str
    args: list[str]
    start_time: str
    end_time: Optional[str] = None
    return_code: Optional[int] = None
    is_running: bool = True


class CommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    handle: Optional[CommandHandle] = None


__all__ = [
    "CommandRequest",
    "CommandResponse",
    "CommandHandle"
]
