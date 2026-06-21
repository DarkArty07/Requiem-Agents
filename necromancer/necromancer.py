"""Necromancer — Orchestrator service. Receives tasks from MCP, delegates to Shades, invokes Revenant."""
import os
import sys
import re
import json
import time
import uuid
import asyncio
from typing import Optional

sys.path.insert(0, os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"))

from shared.opencode_client import chat_completion
from shared.eval import log_agent_call
from necromancer.tools import execute_tool, WRITE_TOOLS, RESEARCH_TOOLS, EXECUTION_TOOLS
from necromancer.revenant import audit

NECROMANCER_MODEL = os.environ.get("NECROMANCER_MODEL", "glm-5.2")
SHADE_MODEL = os.environ.get("SHADE_MODEL", "deepseek-v4-flash")
MAX_REVENANT_RETRIES = 3

TOOL_INSTRUCTIONS_TEMPLATE = """
## Available Tools
You have the following tools available. To use a tool, output a JSON block on its own line:
{{"tool_call": {{"name": "tool_name", "args": {{"arg1": "value1", "arg2": "value2"}}}}}}

Available tools:
{tool_descriptions}

After using a tool, you will see its result. Continue working until the task is complete.
When you are done, write a summary of what you did WITHOUT any tool_call JSON.
"""


def _build_tool_instructions(tools: dict) -> str:
    """Build the tool instructions section for the system prompt based on available tools."""
    descriptions = []
    if "read_file" in tools:
        descriptions.append("- read_file(path): Read a file and return its contents")
    if "write_file" in tools:
        descriptions.append("- write_file(path, content): Write content to a file (creates parent dirs)")
    if "search_files" in tools:
        descriptions.append('- search_files(directory, pattern): Search for files matching a pattern (e.g. "*.py")')
    if "terminal" in tools:
        descriptions.append("- terminal(command): Run a shell command and return output")
    return TOOL_INSTRUCTIONS_TEMPLATE.format(tool_descriptions="\n".join(descriptions))


def parse_tool_calls(content: str) -> list:
    """Parse JSON tool call blocks from model output.

    Looks for {"tool_call": {"name": "...", "args": {...}}} blocks in the text.
    Returns list of {"name": str, "args": dict}.
    """
    results = []
    search_start = 0
    while True:
        idx = content.find('{"tool_call":', search_start)
        if idx == -1:
            break

        # Find the complete JSON object by counting braces
        start = idx
        brace_count = 0
        in_string = False
        escape = False
        end = start
        for i in range(start, len(content)):
            ch = content[i]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if not in_string:
                if ch == "{":
                    brace_count += 1
                elif ch == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break

        if brace_count == 0:
            json_str = content[start:end]
            # Fix model's erroneous single-quote escaping (\\'  -> ')
            json_str = json_str.replace("\\'", "'")
            try:
                parsed = json.loads(json_str, strict=False)
                tc = parsed.get("tool_call", {})
                if tc.get("name") and tc.get("args") is not None:
                    results.append({"name": tc["name"], "args": tc["args"]})
            except (json.JSONDecodeError, ValueError):
                # Fallback: try with single quotes replaced (some models use them)
                try:
                    json_str_fixed = json_str.replace("'", '"')
                    parsed = json.loads(json_str_fixed, strict=False)
                    tc = parsed.get("tool_call", {})
                    if tc.get("name") and tc.get("args") is not None:
                        results.append({"name": tc["name"], "args": tc["args"]})
                except (json.JSONDecodeError, ValueError):
                    pass
            search_start = end
        else:
            # Unbalanced braces — try to repair by appending missing closing braces
            json_str = content[start:]
            json_str = json_str.replace("\\'", "'")
            open_count = 0
            close_count = 0
            repair_in_string = False
            repair_escape = False
            for ch in json_str:
                if repair_escape:
                    repair_escape = False
                    continue
                if ch == "\\":
                    repair_escape = True
                    continue
                if ch == '"' and not repair_escape:
                    repair_in_string = not repair_in_string
                    continue
                if not repair_in_string:
                    if ch == "{":
                        open_count += 1
                    elif ch == "}":
                        close_count += 1
            missing = open_count - close_count
            repaired = False
            if missing > 0:
                json_str += "}" * missing
                try:
                    parsed = json.loads(json_str, strict=False)
                    tc = parsed.get("tool_call", {})
                    if tc.get("name") and tc.get("args") is not None:
                        results.append({"name": tc["name"], "args": tc["args"]})
                        repaired = True
                except (json.JSONDecodeError, ValueError):
                    pass
            if repaired:
                search_start = len(content)
            else:
                # Unbalanced braces — skip past this match to avoid infinite loop
                search_start = idx + len('{"tool_call":')

    return results


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
    """Run a Shade with an agentic loop — model uses tools until done, max 15 iterations."""
    base_system_prompt = load_shade_soul(shade_name)

    # Select tools based on shade
    if shade_name == "programming":
        tools = WRITE_TOOLS
        model = SHADE_MODEL
    elif shade_name == "research":
        tools = RESEARCH_TOOLS
        model = SHADE_MODEL
    elif shade_name == "execution":
        tools = EXECUTION_TOOLS
        model = SHADE_MODEL
    else:
        tools = WRITE_TOOLS
        model = SHADE_MODEL

    # Augment system prompt with tool instructions
    tool_instructions = _build_tool_instructions(tools)
    system_prompt = base_system_prompt + tool_instructions

    print(f"  [Shade {shade_name}] Tools: {list(tools.keys())}", flush=True)

    # Build initial task message
    user_message = f"""## Project Root
{project_root}

## Task
{task}

Execute this task using your tools."""

    messages = [{"role": "user", "content": user_message}]

    total_input_tokens = 0
    total_output_tokens = 0
    start_time = time.time()

    final_content = ""
    iteration_count = 0
    files_written = []

    for iteration in range(15):
        try:
            result = await chat_completion(
                messages=messages,
                model=model,
                system_prompt=system_prompt,
                max_tokens=16384,
            )
        except Exception as e:
            duration = time.time() - start_time
            log_agent_call(
                session_id=session_id,
                agent_name=f"shade_of_{shade_name}",
                action="executed",
                task_id=task_id,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                duration_seconds=duration,
                result="error",
                metadata={"error": str(e), "iteration": iteration},
            )
            return {
                "output": f"Shade error at iteration {iteration}: {e}",
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }

        total_input_tokens += result.get("input_tokens", 0)
        total_output_tokens += result.get("output_tokens", 0)

        content = result["content"]
        final_content = content

        # Parse tool calls from the model response
        tool_calls = parse_tool_calls(content)

        print(f"  [Shade {shade_name}] Iteration {iteration+1}: {len(tool_calls)} tool calls found", flush=True)
        for tc in tool_calls:
            print(f"    -> {tc['name']}({list(tc['args'].keys())})", flush=True)

        if not tool_calls:
            # No more tool calls — Shade is done
            iteration_count = iteration + 1
            break

        # Append assistant response to conversation
        messages.append({"role": "assistant", "content": content})

        # Execute tools and append results
        for tc in tool_calls:
            # Track write_file calls so Revenant can identify created files
            if tc["name"] == "write_file" and "path" in tc["args"]:
                files_written.append(tc["args"]["path"])
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_output = execute_tool(tool_name, tools, **tool_args)
            # Truncate long tool outputs to prevent context explosion
            if len(tool_output) > 2000:
                tool_output = tool_output[:2000] + "\n... (truncated, full output was {} chars)".format(len(tool_output))
            messages.append({"role": "user", "content": f"Tool result ({tool_name}):\n{tool_output}"})

        # Check context budget after this iteration
        if total_input_tokens > 50000:
            print(f"  [Shade {shade_name}] Context budget exceeded ({total_input_tokens} tokens), stopping.", flush=True)
            break

        # Force research shade to write summary at halfway point
        if shade_name == "research" and iteration >= 10:
            messages.append({"role": "user", "content": "You have done enough research. Please write your findings summary now WITHOUT any tool_call JSON. Just output your report."})

        iteration_count = iteration + 1

    duration = time.time() - start_time

    log_agent_call(
        session_id=session_id,
        agent_name=f"shade_of_{shade_name}",
        action="executed",
        task_id=task_id,
        input_tokens=total_input_tokens,
        output_tokens=total_output_tokens,
        duration_seconds=duration,
        result="completed",
        metadata={"iterations": iteration_count},
    )

    # Append file history to output so Revenant can verify
    if files_written:
        final_content += "\n\n## Files Created/Modified\n"
        for fp in files_written:
            final_content += f"- File written: {fp}\n"

    return {
        "output": final_content,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
    }


def _override_shade(shade_name: str, task_text: str) -> str:
    """Override LLM shade selection based on task text pattern matching.
    
    The LLM doesn't always follow routing rules in soul.md.
    This function provides deterministic routing for clear cases.
    """
    task_lower = task_text.lower()
    
    # Execution keywords — running commands, testing, reporting
    execution_patterns = [
        "run pytest", "run tests", "execute tests", "run the test",
        "pytest", "run lint", "run flake", "run mypy",
        "build the project", "compile", "deploy",
        "install dependencies", "pip install", "npm install",
        "run the script", "execute the command", "run the command",
        "start the server", "stop the server",
        "benchmark", "measure performance", "profile",
        "run and report", "execute and report",
    ]
    
    # Creation keywords — writing new code/files
    creation_patterns = [
        "create a class", "create a function", "create a module",
        "write a class", "write a function", "write a script",
        "implement a", "implement the",
        "build a class", "build a function",
        "make a class", "make a function",
    ]
    
    # Research keywords — investigation, reading, analysis
    research_patterns = [
        "investigate", "analyze the code", "analyse the code",
        "read the code", "understand the code",
        "explore the codebase", "explore the project",
        "find bugs", "find issues", "find problems",
        "search for", "look for",
        "review the code", "audit the code",
    ]
    
    # Check execution FIRST — if task is purely about running things
    is_execution = any(p in task_lower for p in execution_patterns)
    is_creation = any(p in task_lower for p in creation_patterns)
    is_research = any(p in task_lower for p in research_patterns)
    
    # If task mentions running tests AND creating code, it's creation (tests come after)
    if is_execution and not is_creation and not is_research:
        return "execution"
    
    # If task is purely research
    if is_research and not is_creation and not is_execution:
        return "research"
    
    # Default: keep LLM's choice (or programming)
    return shade_name


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
- Shade of Execution (runs commands, executes tests, reports results)

Respond in JSON format:
{{
  "subtasks": [
    {{
      "shade": "programming" or "research" or "execution",
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

    print(f"\n[ Necromancer ] Decomposed into {len(subtasks)} subtasks:", flush=True)
    for i, st in enumerate(subtasks):
        print(f"  Subtask {i+1}: shade={st.get('shade', 'programming')}, task={st.get('task', str(st))[:100]}", flush=True)

    # Step 2: Execute subtasks and audit each
    results = []
    for subtask in subtasks:
        shade_name = subtask.get("shade", "programming")
        shade_task = subtask.get("task", str(subtask))
        # Code-level override: fix LLM's shade selection when it doesn't follow routing rules
        original_shade = shade_name
        shade_name = _override_shade(shade_name, shade_task)
        if shade_name != original_shade:
            print(f"  [Routing Override] {original_shade} -> {shade_name} (pattern match)", flush=True)

        retries = 0
        while retries < MAX_REVENANT_RETRIES:
            # Run the Shade
            shade_result = await run_shade(
                shade_name, shade_task, project_root, session_id, task_id
            )

            # Audit with Revenant — now passes project_root and shade_name
            audit_result = await audit(
                shade_result["output"], shade_task, project_root, session_id, task_id, shade_name
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
