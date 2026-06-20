"""Session monitor — visual status for active agents."""
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(
    os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"),
    "shared", "state.db"
)

MODEL_CONTEXT_LIMITS = {
    "deepseek-v4-pro": 262144,
    "glm-5.2": 256000,
    "kimi-k2": 256000,
    "deepseek-v4-flash": 128000,
}


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h}h {m}m"


def _format_tokens(tokens: int) -> str:
    if tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    return str(tokens)


def _progress_bar(percentage: float, width: int = 10) -> str:
    filled = int(percentage / 100 * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def get_session_status() -> str:
    """Get visual status string for all active agents."""
    if not os.path.exists(DB_PATH):
        return "No active sessions — state.db not found"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("""
        SELECT agent_name, 
               SUM(input_tokens + output_tokens) as total_tokens,
               COUNT(*) as calls,
               MIN(timestamp) as first_call,
               MAX(timestamp) as last_call
        FROM agent_calls 
        GROUP BY agent_name
        ORDER BY total_tokens DESC
    """).fetchall()
    
    conn.close()
    
    if not rows:
        return "No active sessions"
    
    lines = []
    for row in rows:
        agent = row["agent_name"]
        tokens = row["total_tokens"] or 0
        model = "unknown"
        
        if agent == "raven":
            model = "deepseek-v4-pro"
        elif agent == "necromancer":
            model = "glm-5.2"
        elif agent == "revenant":
            model = "glm-5.2"
        elif agent.startswith("shade"):
            model = "deepseek-v4-flash"
        
        context_limit = MODEL_CONTEXT_LIMITS.get(model, 128000)
        percentage = (tokens / context_limit * 100) if context_limit > 0 else 0
        
        # Estimate session duration from first to last call
        duration_str = "—"
        if row["first_call"] and row["last_call"]:
            try:
                first = datetime.fromisoformat(row["first_call"].replace("Z", "+00:00"))
                last = datetime.fromisoformat(row["last_call"].replace("Z", "+00:00"))
                duration = (last - first).total_seconds()
                duration_str = _format_duration(duration)
            except Exception:
                pass
        
        bar = _progress_bar(min(percentage, 100))
        tokens_str = f"{_format_tokens(tokens)}/{_format_tokens(context_limit)}"
        
        lines.append(f"{model} | {tokens_str} | {bar} {percentage:.0f}% | {duration_str}")
    
    return "\n".join(lines)
