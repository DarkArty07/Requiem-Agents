"""Revenant — Auditor module. Invoked by Necromancer after each Shade completes."""
import os
import sys
import json
import time

sys.path.insert(0, os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"))

from shared.opencode_client import chat_completion
from shared.eval import log_agent_call

REVENANT_MODEL = os.environ.get("REVENANT_MODEL", "glm-5.2")


def load_soul() -> str:
    soul_path = os.path.join(
        os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"),
        "necromancer", "revenant_soul.md"
    )
    with open(soul_path, "r") as f:
        return f.read()


async def audit(shade_output: str, task_spec: str, session_id: str, task_id: str) -> dict:
    """Audit a Shade's output. Returns dict with verdict, reason, suggestion."""
    system_prompt = load_soul()
    
    user_message = f"""Review the following Shade output for the task specification.

## Task Specification
{task_spec}

## Shade Output
{shade_output}

## Your Review
Provide your verdict in this format:
- VERDICT: PASS or FAIL
- REASON: [if FAIL, specific actionable feedback]
- SUGGESTION: [optional improvement]"""
    
    messages = [{"role": "user", "content": user_message}]
    
    start_time = time.time()
    
    try:
        result = await chat_completion(
            messages=messages,
            model=REVENANT_MODEL,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        
        duration = time.time() - start_time
        content = result["content"]
        
        # Parse verdict
        verdict = "fail"
        if "PASS" in content.upper().split("VERDICT:")[1][:10] if "VERDICT:" in content else False:
            verdict = "pass"
        
        # Log the audit call
        log_agent_call(
            session_id=session_id,
            agent_name="revenant",
            action="audit",
            task_id=task_id,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            duration_seconds=duration,
            result=verdict,
        )
        
        return {
            "verdict": verdict,
            "feedback": content,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        }
    except Exception as e:
        duration = time.time() - start_time
        log_agent_call(
            session_id=session_id,
            agent_name="revenant",
            action="audit",
            task_id=task_id,
            duration_seconds=duration,
            result="error",
            metadata={"error": str(e)},
        )
        return {
            "verdict": "error",
            "feedback": f"Audit error: {e}",
            "input_tokens": 0,
            "output_tokens": 0,
        }
