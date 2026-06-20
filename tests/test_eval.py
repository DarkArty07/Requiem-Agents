"""Tests for shared/eval.py — SQLite telemetry."""

import os
import pytest


def _import_eval():
    """Import shared.eval after env var has been set by temp_db fixture."""
    import importlib
    import shared.eval
    importlib.reload(shared.eval)
    return shared.eval


class TestInitDb:
    def test_init_db(self, temp_db):
        """init_db() creates the agent_calls table."""
        ev = _import_eval()
        ev.init_db()

        conn = ev.get_db()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()

        table_names = [r["name"] for r in tables]
        assert "agent_calls" in table_names


class TestLogAgentCall:
    def test_log_agent_call(self, temp_db):
        """log_agent_call() inserts a row with the expected columns."""
        ev = _import_eval()
        ev.init_db()

        ev.log_agent_call(
            session_id="test-session",
            agent_name="revenant",
            action="audit",
            task_id="task-001",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.005,
            duration_seconds=1.5,
            result="pass",
            metadata={"model": "glm-5.2"},
        )

        conn = ev.get_db()
        rows = conn.execute("SELECT * FROM agent_calls").fetchall()
        conn.close()

        assert len(rows) == 1
        row = rows[0]
        assert row["session_id"] == "test-session"
        assert row["agent_name"] == "revenant"
        assert row["action"] == "audit"
        assert row["task_id"] == "task-001"
        assert row["input_tokens"] == 100
        assert row["output_tokens"] == 50
        assert row["cost_usd"] == 0.005
        assert row["duration_seconds"] == 1.5
        assert row["result"] == "pass"
        assert row["metadata"] is not None
        assert row["timestamp"] is not None


class TestGetEvalReport:
    def test_get_eval_report_empty(self, temp_db):
        """Returns {'total_calls': 0} when no data."""
        ev = _import_eval()
        ev.init_db()

        report = ev.get_eval_report()
        assert report["total_calls"] == 0

    def test_get_eval_report_with_data(self, temp_db):
        """Log 3 calls (2 revenant pass, 1 revenant fail), verify pass_rate=66.7, total_calls=3."""
        ev = _import_eval()
        ev.init_db()

        # Two passing revenant calls
        ev.log_agent_call(
            session_id="s1", agent_name="revenant",
            action="audit", task_id="t1", result="pass",
        )
        ev.log_agent_call(
            session_id="s1", agent_name="revenant",
            action="audit", task_id="t2", result="pass",
        )
        # One failing revenant call
        ev.log_agent_call(
            session_id="s1", agent_name="revenant",
            action="audit", task_id="t3", result="fail",
        )

        report = ev.get_eval_report()
        assert report["total_calls"] == 3
        assert report["total_pass"] == 2
        assert report["total_fail"] == 1
        assert report["audit_pass_rate"] == 66.7

    def test_get_eval_report_cost(self, temp_db):
        """Log calls with cost_usd and verify total_cost_usd sum."""
        ev = _import_eval()
        ev.init_db()

        ev.log_agent_call(
            session_id="s1", agent_name="raven",
            action="chat", cost_usd=0.01,
        )
        ev.log_agent_call(
            session_id="s1", agent_name="necromancer",
            action="decompose", cost_usd=0.02,
        )
        ev.log_agent_call(
            session_id="s1", agent_name="revenant",
            action="audit", cost_usd=0.005,
        )

        report = ev.get_eval_report()
        assert report["total_cost_usd"] == 0.035
