"""Telemetry system — SQLite-based agent call tracking."""
import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(
    os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"),
    "shared", "state.db"
)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            agent_name TEXT NOT NULL,
            action TEXT,
            task_id TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0.0,
            duration_seconds REAL DEFAULT 0.0,
            result TEXT,
            metadata TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_agent_call(
    session_id: str,
    agent_name: str,
    action: str = "",
    task_id: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    duration_seconds: float = 0.0,
    result: str = "",
    metadata: dict = None,
):
    """Log an agent call to SQLite."""
    init_db()
    conn = get_db()
    conn.execute(
        """INSERT INTO agent_calls 
           (timestamp, session_id, agent_name, action, task_id, 
            input_tokens, output_tokens, cost_usd, duration_seconds, 
            result, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(timezone.utc).isoformat(),
            session_id,
            agent_name,
            action,
            task_id,
            input_tokens,
            output_tokens,
            cost_usd,
            duration_seconds,
            result,
            json.dumps(metadata) if metadata else None,
        ),
    )
    conn.commit()
    conn.close()


def get_eval_report() -> dict:
    """Get consolidated metrics from SQLite."""
    init_db()
    conn = get_db()
    
    rows = conn.execute("SELECT * FROM agent_calls").fetchall()
    
    if not rows:
        conn.close()
        return {"total_calls": 0, "message": "No data yet"}
    
    by_agent = {}
    total_cost = 0.0
    total_pass = 0
    total_fail = 0
    escalations = 0
    
    for row in rows:
        name = row["agent_name"]
        if name not in by_agent:
            by_agent[name] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_duration": 0.0,
            }
        by_agent[name]["calls"] += 1
        by_agent[name]["input_tokens"] += row["input_tokens"]
        by_agent[name]["output_tokens"] += row["output_tokens"]
        by_agent[name]["total_duration"] += row["duration_seconds"]
        total_cost += row["cost_usd"]
        
        if row["agent_name"] == "revenant":
            if row["result"] == "pass":
                total_pass += 1
            elif row["result"] == "fail":
                total_fail += 1
            if row["result"] == "escalated":
                escalations += 1
    
    pass_rate = (total_pass / (total_pass + total_fail) * 100) if (total_pass + total_fail) > 0 else 0
    
    for name in by_agent:
        calls = by_agent[name]["calls"]
        by_agent[name]["avg_duration"] = by_agent[name]["total_duration"] / calls if calls > 0 else 0
    
    conn.close()
    
    return {
        "total_calls": len(rows),
        "by_agent": by_agent,
        "total_cost_usd": round(total_cost, 4),
        "audit_pass_rate": round(pass_rate, 1),
        "total_pass": total_pass,
        "total_fail": total_fail,
        "escalations": escalations,
    }
