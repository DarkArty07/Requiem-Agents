"""Revenant — Auditor module. Invoked by Necromancer after each Shade completes."""
import os
import sys
import re
import json
import time
import subprocess

sys.path.insert(0, os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"))

from shared.opencode_client import chat_completion
from shared.eval import log_agent_call
from necromancer.tools import read_file as tools_read_file

REVENANT_MODEL = os.environ.get("REVENANT_MODEL", "glm-5.2")


def load_soul() -> str:
    soul_path = os.path.join(
        os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem"),
        "necromancer", "revenant_soul.md"
    )
    with open(soul_path, "r") as f:
        return f.read()


def extract_file_paths(text: str, project_root: str) -> list:
    """Extract likely file paths from Shade output text.

    Scans for:
    - Lines with "File written:", "File created:", etc. followed by a path
    - Absolute paths under project_root
    - Lines ending in known source extensions that exist on disk
    """
    paths = set()

    # Pattern: "File written: /path/to/file" or "File created: /path" etc.
    for match in re.finditer(
        r'(?:File written:|File created:|Modified:|Created:|Written to:|Wrote)\s*(\S+)',
        text,
        re.IGNORECASE,
    ):
        candidate = match.group(1).rstrip(".,;:")
        if os.path.isfile(candidate):
            paths.add(candidate)

    # Pattern: absolute paths under project_root (e.g. /home/prometeo/Requiem/some/file.py)
    escaped_root = re.escape(project_root)
    for match in re.finditer(rf'{escaped_root}\S+', text):
        candidate = match.group(0).rstrip(".,;:")
        if os.path.isfile(candidate):
            paths.add(candidate)

    # Pattern: lines starting with / that exist as files on disk
    for line in text.split('\n'):
        stripped = line.strip().rstrip(".,;:")
        if stripped.startswith('/'):
            # Could be an absolute path — verify it exists
            if os.path.isfile(stripped):
                paths.add(stripped)

    return sorted(paths)


def compile_py_file(filepath: str) -> str:
    """Run python -m py_compile on a file, return result string."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return f"- {filepath}: OK (syntax valid)"
        else:
            stderr = result.stderr.strip() or "(no stderr output)"
            return f"- {filepath}: SYNTAX ERROR\n  {stderr}"
    except subprocess.TimeoutExpired:
        return f"- {filepath}: TIMEOUT (py_compile exceeded 30s)"
    except Exception as e:
        return f"- {filepath}: ERROR — {e}"


def parse_verdict(content: str) -> str:
    """Robustly parse a VERDICT: PASS or VERDICT: FAIL from Revenant output.

    Searches line by line for VERDICT markers, then falls back to last-200
    char scan for standalone PASS/FAIL tokens.
    """
    content_upper = content.upper()
    # Look for VERDICT: PASS or VERDICT: FAIL on individual lines
    for line in content.split('\n'):
        line_upper = line.upper()
        if 'VERDICT:' in line_upper:
            if 'PASS' in line_upper:
                return "pass"
            elif 'FAIL' in line_upper:
                return "fail"
    # Fallback: look for standalone PASS/FAIL in the last 200 chars
    last_200 = content_upper[-200:]
    has_pass = 'PASS' in last_200
    has_fail = 'FAIL' in last_200
    if has_pass and not has_fail:
        return "pass"
    if has_fail:
        return "fail"
    return "fail"  # Default to fail if unclear


async def audit(
    shade_output: str,
    task_spec: str,
    project_root: str,
    session_id: str,
    task_id: str,
    shade_name: str = "programming",
) -> dict:
    """Audit a Shade's output. Reads actual files and compiles .py to verify work.

    Returns dict with verdict, feedback, and token counts.
    """
    system_prompt = load_soul()
    start_time = time.time()

    # Extract file paths from Shade output and read actual files
    file_paths = extract_file_paths(shade_output, project_root)

    # Check if Shade ran terminal commands (don't auto-fail if it did useful execution work)
    has_terminal_output = "Tool result (terminal):" in shade_output or "tool_result" in shade_output.lower()

    # Pre-check: if task requires creating files but none exist, auto-fail
    task_lower = task_spec.lower()
    creation_words = ['create', 'write', 'implement', 'build', 'add', 'generate']
    is_creation_task = any(w in task_lower for w in creation_words)
    execution_words = ['run', 'test', 'execute', 'check', 'find', 'report', 'lint', 'pytest', 'audit', 'diagnose']
    is_execution_task = any(w in task_lower for w in execution_words)
    if shade_name == "programming" and is_creation_task and not is_execution_task and not file_paths and not has_terminal_output:
        duration = time.time() - start_time
        log_agent_call(
            session_id=session_id, agent_name='revenant',
            action='audit', task_id=task_id,
            duration_seconds=duration, result='fail',
        )
        return {
            'verdict': 'fail',
            'feedback': 'No files were created. For a task that requires creating code, you MUST use write_file to create the actual files. Do not describe what you would do — USE write_file to create the files NOW.',
            'input_tokens': 0, 'output_tokens': 0,
        }

    file_contents = ""
    compile_results = ""
    for fp in file_paths:
        if os.path.isfile(fp):
            content = tools_read_file(fp)
            file_contents += f"\n### {fp}\n```\n{content}\n```\n"

            # Compile .py files
            if fp.endswith('.py'):
                compile_results += compile_py_file(fp) + "\n"

    if not file_contents:
        if is_execution_task and not file_paths:
            file_contents = "(Execution task — no files expected)"
        else:
            file_contents = "(No files found to verify — Shade may not have created any files, or paths could not be extracted.)"

    if not compile_results:
        compile_results = "(No .py files to compile.)"

    task_context = "This was an execution task. Verify the command output is complete and accurate. DO NOT fail because tests have failures — judge whether the Shade ran the commands and reported results correctly." if is_execution_task else ""

    print(f"  [Revenant] is_creation={is_creation_task}, is_execution={is_execution_task}, has_files={bool(file_paths)}, has_terminal={has_terminal_output}", flush=True)

    user_message = f"""Review the following Shade output for the task specification.

{task_context}

## Task Specification
{task_spec}

## Shade Output
{shade_output}

## Actual Files Created/Modified
{file_contents}

## Compile Results
{compile_results}

## Your Review
Provide your verdict in this format:
- VERDICT: PASS or FAIL
- REASON: [if FAIL, specific actionable feedback]
- SUGGESTION: [optional improvement]"""

    messages = [{"role": "user", "content": user_message}]

    try:
        result = await chat_completion(
            messages=messages,
            model=REVENANT_MODEL,
            system_prompt=system_prompt,
            max_tokens=4096,
        )

        duration = time.time() - start_time
        content = result["content"]

        # Parse verdict using robust parser
        verdict = parse_verdict(content)

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
