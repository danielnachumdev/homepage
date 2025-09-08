from pydantic import BaseModel
from typing import Optional, List


class CommandRequest(BaseModel):
    command: str


class CommandResult(BaseModel):
    """Comprehensive result object for command execution."""
    args: List[str]
    returncode: int
    stdout: str
    stderr: str
    pid: int
    start_time: str
    end_time: str
    duration_seconds: float
    timeout_occurred: bool
    killed: bool
    success: bool
    command: str  # The original command string


class CommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    result: Optional[CommandResult] = None


__all__ = [
    "CommandRequest",
    "CommandResponse",
    "CommandResult"
]
