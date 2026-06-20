"""Tests for dashboard-api/server.py — FastAPI backend.

These tests set REQUIEM_PROJECT_ROOT to a temp directory so no real state.db
or config.json is touched. The server module is imported fresh after the
env var is set so that DB_PATH, CONFIG_PATH, and project_root all point to the
temp directory.

NOTE: dashboard-api/ uses a hyphen, so we can't import it as a Python package.
We add its parent dir to sys.path and import the file directly via importlib.
"""

import os
import sys
import json
import importlib.util
import pytest
from pathlib import Path
from fastapi.testclient import TestClient


# Absolute path to the real dashboard-api directory
_DASHBOARD_API_DIR = os.path.join(
    os.environ.get("REQUIEM_PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "dashboard-api"
)
_SERVER_PATH = os.path.join(_DASHBOARD_API_DIR, "server.py")


@pytest.fixture
def app(tmp_path):
    """Set up env, create temp shared dir, import server file, return TestClient(app)."""
    old_root = os.environ.get("REQUIEM_PROJECT_ROOT")
    os.environ["REQUIEM_PROJECT_ROOT"] = str(tmp_path)

    # Create shared/ dir so sqlite can create state.db
    (tmp_path / "shared").mkdir(parents=True, exist_ok=True)

    # Purge cached shared modules so they see the new REQUIEM_PROJECT_ROOT
    for mod in list(sys.modules.keys()):
        if mod == "shared" or mod.startswith("shared."):
            del sys.modules[mod]
    if "server" in sys.modules:
        del sys.modules["server"]

    # Add the real dashboard-api dir to sys.path so imports within server.py work
    if _DASHBOARD_API_DIR not in sys.path:
        sys.path.insert(0, _DASHBOARD_API_DIR)
    # Also add tmp_path (project root) so shared modules are found at the new root level
    if str(tmp_path) not in sys.path:
        sys.path.insert(0, str(tmp_path))

    # Load server.py from its real path
    spec = importlib.util.spec_from_file_location("server", _SERVER_PATH)
    srv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(srv)
    client = TestClient(srv.app)

    yield client

    # Cleanup
    if old_root is None:
        del os.environ["REQUIEM_PROJECT_ROOT"]
    else:
        os.environ["REQUIEM_PROJECT_ROOT"] = old_root


class TestSessions:
    def test_get_sessions_empty(self, app):
        """GET /api/sessions returns agents list (empty when no DB)."""
        response = app.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data


class TestStats:
    def test_get_stats(self, app, tmp_path):
        """GET /api/stats returns a report dict."""
        # Initialize DB with a call so it's not empty
        from shared.eval import init_db, log_agent_call
        init_db()
        log_agent_call(session_id="s1", agent_name="raven", action="chat", result="pass")

        response = app.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_calls" in data
        assert data["total_calls"] >= 1


class TestConfig:
    def test_get_config(self, app):
        """GET /api/config returns default config with raven, necromancer, revenant keys."""
        response = app.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "raven" in data
        assert "necromancer" in data
        assert "revenant" in data

    def test_post_config(self, app, tmp_path):
        """POST /api/config with update, verify response has updated value."""
        response = app.post("/api/config", json={"config": {"raven": "glm-5.2"}})
        assert response.status_code == 200
        data = response.json()
        assert data["raven"] == "glm-5.2"

        # Verify persisted
        config_path = tmp_path / "shared" / "config.json"
        assert config_path.exists()
        saved = json.loads(config_path.read_text())
        assert saved["raven"] == "glm-5.2"


class TestActivity:
    def test_get_activity(self, app):
        """GET /api/activity returns activity list."""
        response = app.get("/api/activity")
        assert response.status_code == 200
        data = response.json()
        assert "activity" in data
