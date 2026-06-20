"""Structural tests for Necromancer logic — no API calls needed.

Tests module imports, tool registries, and that prompt/markdown files exist.
"""

import os
import sys
import pytest

PROJECT_ROOT = os.environ.get(
    "REQUIEM_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)


class TestNecromancerImport:
    """Test that necromancer.py can be imported (syntax check)."""

    def test_import_tools(self):
        """At minimum, tools.py must import cleanly (no API deps)."""
        import necromancer.tools
        assert hasattr(necromancer.tools, "read_file")

    def test_necromancer_service_syntax(self):
        """Check that necromancer.py parses correctly by compiling it."""
        path = os.path.join(PROJECT_ROOT, "necromancer", "necromancer.py")
        with open(path) as f:
            source = f.read()
        compile(source, path, "exec")  # raises SyntaxError on failure

    def test_revenant_syntax(self):
        """Check that revenant.py parses correctly."""
        path = os.path.join(PROJECT_ROOT, "necromancer", "revenant.py")
        with open(path) as f:
            source = f.read()
        compile(source, path, "exec")


class TestToolRegistries:
    """Test the tool registry constants."""

    def test_all_tools_defined(self):
        from necromancer.tools import ALL_TOOLS, WRITE_TOOLS, RESEARCH_TOOLS
        assert len(ALL_TOOLS) >= 4
        assert len(WRITE_TOOLS) >= 4
        assert len(RESEARCH_TOOLS) >= 2

    def test_execute_tool_registry(self):
        from necromancer.tools import execute_tool, ALL_TOOLS
        result = execute_tool("read_file", ALL_TOOLS, path=__file__)
        assert "test_execute_tool_registry" in result


class TestShadePrompts:
    """Test that shade system prompts (.md files) exist and are non-empty."""

    SHADE_FILES = ["programming.md", "research.md"]

    @pytest.mark.parametrize("shade_file", SHADE_FILES)
    def test_shade_prompt_exists(self, shade_file):
        path = os.path.join(PROJECT_ROOT, "necromancer", "shades", shade_file)
        assert os.path.exists(path), f"Missing shade prompt: {path}"
        with open(path) as f:
            content = f.read()
        assert len(content.strip()) > 0, f"Empty shade prompt: {path}"

    def test_revenant_soul_exists(self):
        """Test that revenant_soul.md exists and is non-empty."""
        path = os.path.join(PROJECT_ROOT, "necromancer", "revenant_soul.md")
        assert os.path.exists(path), f"Missing revenant_soul.md: {path}"
        with open(path) as f:
            content = f.read()
        assert len(content.strip()) > 0

    def test_necromancer_soul_exists(self):
        """Test that necromancer soul.md exists."""
        path = os.path.join(PROJECT_ROOT, "necromancer", "soul.md")
        assert os.path.exists(path)
        with open(path) as f:
            content = f.read()
        assert len(content.strip()) > 0


class TestDashboardApiImport:
    """Structural tests for dashboard-api (no real server start)."""

    def test_dashboard_api_syntax(self):
        """Check dashboard-api/server.py parses correctly."""
        path = os.path.join(PROJECT_ROOT, "dashboard-api", "server.py")
        with open(path) as f:
            source = f.read()
        compile(source, path, "exec")


class TestMcpServerImport:
    """Structural tests for the MCP server."""

    def test_mcp_server_syntax(self):
        """Check requiem-mcp/server.py parses correctly."""
        path = os.path.join(PROJECT_ROOT, "requiem-mcp", "server.py")
        with open(path) as f:
            source = f.read()
        compile(source, path, "exec")
