"""Minimal FastAPI Time API.

This module provides a simple FastAPI application with endpoints to check
health and retrieve the current UTC time.
"""

from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict:
    """Health check endpoint.

    Returns:
        dict: A dictionary with a status message indicating the service is
            operational.
            Example: {"status": "ok"}
    """
    return {"status": "ok"}


@app.get("/time")
def get_time() -> dict:
    """Retrieve the current UTC time.

    Returns:
        dict: A dictionary containing:
            - current_time (str): ISO 8601 formatted UTC time.
            - timezone (str): Always "UTC".
            - timestamp (float): POSIX timestamp of the current UTC time.
    """
    current_utc = datetime.now(timezone.utc)
    return {
        "current_time": current_utc.isoformat(),
        "timezone": "UTC",
        "timestamp": current_utc.timestamp(),
    }
