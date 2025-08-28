from pydantic import BaseModel
from typing import Optional


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None


__all__ = [
    "CommandRequest",
    "CommandResponse"
]
