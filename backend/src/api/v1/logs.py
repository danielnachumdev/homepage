from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import os
import json
from datetime import datetime

router = APIRouter(prefix="/logs", tags=["logs"])

# Frontend logs directory
frontend_log_dir = r"C:\Users\User\Desktop\Programing\VCS\homepage\frontend\logs"
os.makedirs(frontend_log_dir, exist_ok=True)


class LogEntry(BaseModel):
    timestamp: str
    name: str
    level: str
    message: str
    module: str = ""
    function: str = ""
    line: int = 0
    args: List[Any] = []
    extra: Dict[str, Any] = {}


class LogsRequest(BaseModel):
    logs: List[str]


class LogsResponse(BaseModel):
    success: bool
    message: str
    received_count: int


@router.post("/", response_model=LogsResponse)
async def receive_logs(request: LogsRequest):
    """Receive logs from frontend and save them to frontend logs directory"""
    try:
        received_count = 0

        # Create frontend log file path
        frontend_log_file = os.path.join(frontend_log_dir, f"frontend-{datetime.now().strftime('%Y-%m-%d')}.log")

        for log_entry in request.logs:
            try:
                # Parse JSON formatted log entry
                log_data = json.loads(log_entry)

                # Create a formatted log record
                timestamp = log_data.get('timestamp', '')
                level = log_data.get('level', 'INFO')
                name = log_data.get('name', 'unknown')
                message = log_data.get('message', '')
                module = log_data.get('module', '')
                function = log_data.get('function', '')
                line = log_data.get('line', 0)

                # Format the log entry for file storage
                log_record = f"{timestamp} - {level} - {name} - {message}"
                if module:
                    log_record += f" [{module}"
                    if function:
                        log_record += f".{function}"
                    if line:
                        log_record += f":{line}"
                    log_record += "]"

                # Add extra context if available
                extra = log_data.get('extra', {})
                if extra:
                    log_record += f" {extra}"

                # Write directly to frontend log file
                with open(frontend_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{log_record}\n")

                received_count += 1

            except json.JSONDecodeError:
                # If JSON parsing fails, treat as plain text log
                with open(frontend_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Plain text log: {log_entry}\n")
                received_count += 1

            except Exception as e:
                # If any other error occurs, log the raw entry
                with open(frontend_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Error processing log: {log_entry}, error: {e}\n")
                received_count += 1

        return LogsResponse(
            success=True,
            message=f"Successfully received {received_count} log entries",
            received_count=received_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process logs: {str(e)}"
        )


@router.get("/health")
async def logs_health():
    """Health check for logs endpoint"""
    frontend_log_file = os.path.join(frontend_log_dir, f"frontend-{datetime.now().strftime('%Y-%m-%d')}.log")
    return {"status": "healthy", "log_file": frontend_log_file}


__all__ = ["router"]
