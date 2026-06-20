"""Requiem Dashboard API — FastAPI backend serving telemetry data."""
import sys
import os
import json
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Bootstrap ────────────────────────────────────────────────────────────────
project_root = os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem")
sys.path.insert(0, project_root)

from shared.eval import get_eval_report, DB_PATH
from shared.session_monitor import MODEL_CONTEXT_LIMITS

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Requiem Agents Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_PATH = os.path.join(project_root, "shared", "config.json")

DEFAULT_CONFIG = {
    "raven": "deepseek-v4-pro",
    "necromancer": "glm-5.2",
    "revenant": "glm-5.2",
    "shade-programming": "deepseek-v4-flash",
    "shade-research": "deepseek-v4-flash",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return dict(DEFAULT_CONFIG)


def _save_config(cfg: dict) -> dict:
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    return cfg


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/sessions")
def get_sessions():
    """Return active agents with token usage, model, context %."""
    if not os.path.exists(DB_PATH):
        return {"agents": [], "message": "No data yet"}

    conn = _get_db()
    rows = conn.execute("""
        SELECT agent_name,
               SUM(input_tokens + output_tokens) as total_tokens,
               SUM(input_tokens) as total_input,
               SUM(output_tokens) as total_output,
               COUNT(*) as calls,
               MIN(timestamp) as first_call,
               MAX(timestamp) as last_call
        FROM agent_calls
        GROUP BY agent_name
        ORDER BY total_tokens DESC
    """).fetchall()
    conn.close()

    agents = []
    for row in rows:
        agent = row["agent_name"]

        if agent == "raven":
            model = "deepseek-v4-pro"
        elif agent == "necromancer":
            model = "glm-5.2"
        elif agent == "revenant":
            model = "glm-5.2"
        elif agent in ("shade-programming", "shade-research") or agent.startswith("shade"):
            model = "deepseek-v4-flash"
        else:
            model = "unknown"

        context_limit = MODEL_CONTEXT_LIMITS.get(model, 128000)
        total_tokens = row["total_tokens"] or 0
        context_pct = round((total_tokens / context_limit * 100), 1) if context_limit > 0 else 0

        duration = None
        if row["first_call"] and row["last_call"]:
            try:
                first = datetime.fromisoformat(row["first_call"].replace("Z", "+00:00"))
                last = datetime.fromisoformat(row["last_call"].replace("Z", "+00:00"))
                duration = round((last - first).total_seconds(), 1)
            except Exception:
                pass

        agents.append({
            "agent_name": agent,
            "model": model,
            "calls": row["calls"],
            "total_tokens": total_tokens,
            "total_input": row["total_input"] or 0,
            "total_output": row["total_output"] or 0,
            "context_limit": context_limit,
            "context_pct": context_pct,
            "duration_seconds": duration,
        })

    return {"agents": agents}


@app.get("/api/stats")
def get_stats():
    """Return eval report."""
    report = get_eval_report()
    return report


@app.get("/api/activity")
def get_activity():
    """Return last 50 agent calls."""
    if not os.path.exists(DB_PATH):
        return {"activity": []}

    conn = _get_db()
    rows = conn.execute("""
        SELECT timestamp, agent_name, action, result, duration_seconds,
               input_tokens, output_tokens, cost_usd, task_id
        FROM agent_calls
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()
    conn.close()

    activity = []
    for row in rows:
        activity.append({
            "timestamp": row["timestamp"],
            "agent_name": row["agent_name"],
            "action": row["action"],
            "result": row["result"],
            "duration_seconds": row["duration_seconds"],
            "input_tokens": row["input_tokens"],
            "output_tokens": row["output_tokens"],
            "cost_usd": row["cost_usd"],
            "task_id": row["task_id"],
        })

    return {"activity": activity}


@app.get("/api/config")
def get_config():
    """Return current agent config."""
    return _load_config()


class ConfigUpdate(BaseModel):
    config: dict


@app.post("/api/config")
def post_config(update: ConfigUpdate):
    """Update agent config."""
    current = _load_config()
    for key, value in update.config.items():
        current[key] = value
    _save_config(current)
    return current


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=True)
