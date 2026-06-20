import time

from fastapi.testclient import TestClient
from src.time_api import app

client = TestClient(app)


def test_health_returns_ok():
    """Test that health endpoint returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_json():
    """Test that health endpoint returns JSON content type."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


def test_time_returns_200():
    """Test that time endpoint returns 200."""
    response = client.get("/time")
    assert response.status_code == 200


def test_time_has_correct_fields():
    """Test that time response contains all required fields."""
    response = client.get("/time")
    data = response.json()
    assert "current_time" in data
    assert "timezone" in data
    assert "timestamp" in data


def test_time_timezone_is_utc():
    """Test that time response timezone is UTC."""
    response = client.get("/time")
    assert response.json()["timezone"] == "UTC"


def test_time_timestamp_is_recent():
    """Test that timestamp in response is within 5 seconds of current time."""
    response = client.get("/time")
    assert abs(response.json()["timestamp"] - time.time()) <= 5


def test_nonexistent_endpoint_returns_404():
    """Test that a nonexistent endpoint returns 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
