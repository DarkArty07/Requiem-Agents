"""Requiem MCP Server — bridge between Raven and the Necromancer."""
import sys
import os
import uuid
import asyncio

project_root = os.environ.get("REQUIEM_PROJECT_ROOT", "/home/prometeo/Requiem")
sys.path.insert(0, project_root)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from shared.eval import get_eval_report, init_db, log_agent_call
from shared.session_monitor import get_session_status
from necromancer.necromancer import process_task

server = Server("requiem-mcp")
_active_tasks = {}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="activate_necromancer",
            description="Activate the Necromancer orchestrator with a formal task. Requires project_root and project_name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {"type": "string", "description": "Absolute path to the project root. REQUIRED."},
                    "project_name": {"type": "string", "description": "Name of the project. REQUIRED."},
                    "formal_task": {"type": "string", "description": "The formalized requirements."},
                },
                "required": ["project_root", "project_name", "formal_task"],
            },
        ),
        Tool(
            name="check_task_status",
            description="Check the status of a task delegated to the Necromancer.",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "Task ID from activate_necromancer."}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="check_session_status",
            description="Get visual status of all active agents.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_eval_report",
            description="Get consolidated telemetry metrics.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="shutdown_necromancer",
            description="Shut down the Necromancer.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "activate_necromancer":
        project_root_arg = arguments.get("project_root", "")
        project_name = arguments.get("project_name", "")
        formal_task = arguments.get("formal_task", "")
        
        if not project_root_arg or not project_name:
            return [TextContent(type="text", text="ERROR: project_root and project_name are REQUIRED.")]
        
        session_id = str(uuid.uuid4())
        
        # Run the Necromancer
        result = await process_task(
            project_root=project_root_arg,
            project_name=project_name,
            formal_task=formal_task,
            session_id=session_id,
        )
        
        task_id = result["task_id"]
        _active_tasks[task_id] = result
        
        # Format results for Raven
        lines = [f"Necromancer completed task {task_id} for '{project_name}'", "=" * 50]
        for r in result["results"]:
            lines.append(f"\n[Shade of {r['shade']}] Audit: {r['audit']}")
            lines.append(r["output"][:2000])
            if r.get("escalated"):
                lines.append(f"\n⚠ ESCALATED to Raven: {r.get('feedback', '')[:500]}")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "check_task_status":
        task_id = arguments.get("task_id", "")
        if task_id in _active_tasks:
            return [TextContent(type="text", text=f"Task {task_id}: completed")]
        return [TextContent(type="text", text=f"Task {task_id}: not found or in_progress")]
    
    elif name == "check_session_status":
        return [TextContent(type="text", text=get_session_status())]
    
    elif name == "get_eval_report":
        report = get_eval_report()
        lines = ["Requiem Agents — Eval Report", "=" * 40, f"Total calls: {report.get('total_calls', 0)}"]
        if "by_agent" in report:
            lines.append("")
            for agent, stats in report["by_agent"].items():
                lines.append(f"  {agent}: {stats['calls']} calls, {stats['input_tokens'] + stats['output_tokens']} tokens")
        if "total_cost_usd" in report:
            lines.append(f"\nTotal cost: ${report['total_cost_usd']}")
        if "audit_pass_rate" in report:
            lines.append(f"Audit pass rate: {report['audit_pass_rate']}%")
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "shutdown_necromancer":
        _active_tasks.clear()
        return [TextContent(type="text", text="Necromancer shut down.")]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    init_db()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
