"""Necromancer — Orchestrator service. Receives tasks from MCP, delegates to Shades, invokes Revenant."""
import os
import sys
import json
import time
import uuid
import asyncio
from typing import Optional

sys.path.insert(0, os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"))

from shared.opencode_client import chat_completion
from shared.eval import log_agent_call
from necromancer.tools import execute_tool, WRITE_TOOLS, RESEARCH_TOOLS
from necromancer.revenant import audit

NECROMANCER_MODEL = os.environ.get("NECROMANCER_MODEL", "glm-5.2")
SHADE_MODEL = os.environ.get("SHADE_MODEL", "deepseek-v4-flash")
MAX_REVENANT_RETRIES = 3


def load_soul(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def load_shade_soul(shade_name: str) -> str:
    """Load a Shade's system prompt from shades/ directory."""
    root = os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem")
    path = os.path.join(root, "necromancer", "shades", f"{shade_name}.md")
    return load_soul(path)


async def run_shade(
    shade_name: str,
    task: str,
    project_root: str,
    session_id: str,
    task_id: str,
) -> dict:
    """Run a Shade with its system prompt and tools."""
    system_prompt = load_shade_soul(shade_name)
    
    # Select tools based on shade
    if shade_name == "programming":
        tools = WRITE_TOOLS
        model = SHADE_MODEL
    elif shade_name == "research":
        tools = RESEARCH_TOOLS
        model = SHADE_MODEL
    else:
        tools = WRITE_TOOLS
        model = SHADE_MODEL
    
    # Build the prompt with task context
    user_message = f"""## Project Root
{project_root}

## Task
{task}

Execute this task. Use your tools as needed. Report what you did."""
    
    messages = [{"role": "user", "content": user_message}]
    
    start_time = time.time()
    
    try:
        result = await chat_completion(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            max_tokens=16384,
        )
        
        duration = time.time() - start_time
        
        log_agent_call(
            session_id=session_id,
            agent_name=f"shade_of_{shade_name}",
            action="executed",
            task_id=task_id,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            duration_seconds=duration,
            result="completed",
        )
        
        return {
            "output": result["content"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        }
    except Exception as e:
        duration = time.time() - start_time
        log_agent_call(
            session_id=session_id,
            agent_name=f"shade_of_{shade_name}",
            action="executed",
            task_id=task_id,
            duration_seconds=duration,
            result="error",
            metadata={"error": str(e)},
        )
        return {
            "output": f"Shade error: {e}",
            "input_tokens": 0,
            "output_tokens": 0,
        }


async def process_task(
    project_root: str,
    project_name: str,
    formal_task: str,
    session_id: str,
) -> dict:
    """Process a task: decompose, delegate to Shades, audit with Revenant."""
    task_id = str(uuid.uuid4())
    
    # Log Necromancer activation
    log_agent_call(
        session_id=session_id,
        agent_name="necromancer",
        action="activated",
        task_id=task_id,
        result="started",
        metadata={"project_root": project_root, "project_name": project_name},
    )
    
    # Step 1: Necromancer decomposes the task
    necro_soul = load_soul(os.path.join(
        os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"),
        "necromancer", "soul.md"
    ))
    
    decompose_prompt = f"""## Project: {project_name}
## Root: {project_root}

## Task from Raven
{formal_task}

## Your Job
Decompose this task into subtasks for your Shades. Available Shades:
- Shade of Programming (writes code, modifies files, runs commands)
- Shade of Research (reads code, searches files, investigates)

Respond in JSON format:
{{
  "subtasks": [
    {{
      "shade": "programming" or "research",
      "task": "specific task description"
    }}
  ]
}}"""
    
    necro_result = await chat_completion(
        messages=[{"role": "user", "content": decompose_prompt}],
        model=NECROMANCER_MODEL,
        system_prompt=necro_soul,
        max_tokens=4096,
    )
    
    log_agent_call(
        session_id=session_id,
        agent_name="necromancer",
        action="decomposed",
        task_id=task_id,
        input_tokens=necro_result["input_tokens"],
        output_tokens=necro_result["output_tokens"],
        result="completed",
    )
    
    # Parse subtasks (best effort JSON parse)
    subtasks = []
    try:
        # Try to extract JSON from the response
        content = necro_result["content"]
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            subtasks = parsed.get("subtasks", [])
    except (json.JSONDecodeError, ValueError):
        pass
    
    if not subtasks:
        # Fallback: single task to programming shade
        subtasks = [{"shade": "programming", "task": formal_task}]
    
    # Step 2: Execute subtasks and audit each
    results = []
    for subtask in subtasks:
        shade_name = subtask.get("shade", "programming")
        shade_task = subtask.get("task", str(subtask))
        
        retries = 0
        while retries < MAX_REVENANT_RETRIES:
            # Run the Shade
            shade_result = await run_shade(
                shade_name, shade_task, project_root, session_id, task_id
            )
            
            # Audit with Revenant
            audit_result = await audit(
                shade_result["output"], shade_task, session_id, task_id
            )
            
            if audit_result["verdict"] == "pass":
                results.append({
                    "shade": shade_name,
                    "output": shade_result["output"],
                    "audit": "pass",
                })
                break
            elif audit_result["verdict"] == "error":
                results.append({
                    "shade": shade_name,
                    "output": shade_result["output"],
                    "audit": "error",
                    "feedback": audit_result["feedback"],
                })
                break
            else:
                # FAIL — retry with feedback
                retries += 1
                shade_task = f"""Original task: {shade_task}

Revenant feedback (attempt {retries}/{MAX_REVENANT_RETRIES}):
{audit_result['feedback']}

Please fix the issues and redo the task."""
        
        if retries >= MAX_REVENANT_RETRIES:
            # Escalate to Raven
            log_agent_call(
                session_id=session_id,
                agent_name="necromancer",
                action="escalated",
                task_id=task_id,
                result="escalated",
                metadata={"reason": "3 Revenant rejections", "shade": shade_name},
            )
            results.append({
                "shade": shade_name,
                "output": shade_result["output"],
                "audit": "failed_3_times",
                "feedback": audit_result["feedback"],
                "escalated": True,
            })
    
    # Log completion
    log_agent_call(
        session_id=session_id,
        agent_name="necromancer",
        action="completed",
        task_id=task_id,
        result="completed",
    )
    
    return {
        "task_id": task_id,
        "results": results,
    }
