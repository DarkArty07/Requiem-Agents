"""Custom tools for Necromancer and Shades — no hermes-agent dependency."""
import os
import subprocess
import asyncio
from typing import Optional


def read_file(path: str, max_lines: int = 500) -> str:
    """Read a file and return its contents."""
    if not os.path.exists(path):
        return f"Error: File not found: {path}"
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            return "".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines truncated)"
        return "".join(lines)
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w") as f:
            f.write(content)
        return f"File written: {path} ({len(content)} bytes)"
    except Exception as e:
        return f"Error writing file: {e}"


def search_files(directory: str, pattern: str, max_results: int = 20) -> str:
    """Search for files matching a pattern in a directory."""
    import fnmatch
    results = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden dirs and common ignores
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".venv", ".git")]
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                results.append(os.path.join(root, filename))
                if len(results) >= max_results:
                    break
    if not results:
        return f"No files matching '{pattern}' in {directory}"
    return "\n".join(results)


def run_terminal(command: str, cwd: Optional[str] = None, timeout: int = 30) -> str:
    """Run a terminal command and return output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=cwd, timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}" if result.stdout else result.stderr
        if not output:
            output = f"(command completed, exit code {result.returncode})"
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"


# Tool registry — maps tool names to functions
# Each agent gets a subset of these based on their role
ALL_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "search_files": search_files,
    "terminal": run_terminal,
}

READ_ONLY_TOOLS = {
    "read_file": read_file,
    "search_files": search_files,
}

WRITE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "search_files": search_files,
    "terminal": run_terminal,
}

RESEARCH_TOOLS = {
    "read_file": read_file,
    "search_files": search_files,
}

EXECUTION_TOOLS = {
    "read_file": read_file,
    "search_files": search_files,
    "terminal": run_terminal,
}


def execute_tool(tool_name: str, tool_registry: dict, **kwargs) -> str:
    """Execute a tool from a registry."""
    func = tool_registry.get(tool_name)
    if not func:
        return f"Error: Tool '{tool_name}' not available"
    try:
        return func(**kwargs)
    except Exception as e:
        return f"Error executing {tool_name}: {e}"
