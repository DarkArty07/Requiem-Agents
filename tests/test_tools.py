"""Tests for necromancer/tools.py — custom tools."""

import os
import pytest

from necromancer.tools import (
    read_file,
    write_file,
    search_files,
    run_terminal,
    execute_tool,
    ALL_TOOLS,
    WRITE_TOOLS,
    RESEARCH_TOOLS,
    READ_ONLY_TOOLS,
)


class TestReadFile:
    def test_read_file(self, tmp_path):
        """Create temp file, read it, verify content."""
        f = tmp_path / "test.txt"
        f.write_text("hello world\nline2")
        result = read_file(str(f))
        assert "hello world" in result
        assert "line2" in result

    def test_read_file_not_found(self):
        """Returns error message for missing file."""
        result = read_file("/nonexistent/path/file.txt")
        assert "Error" in result or "not found" in result.lower()


class TestWriteFile:
    def test_write_file(self, tmp_path):
        """Write to temp path, verify content on disk."""
        f = tmp_path / "output.txt"
        result = write_file(str(f), "test content here")
        assert "File written" in result
        assert f.read_text() == "test content here"

    def test_write_file_creates_dirs(self, tmp_path):
        """Write to a nested path, verify directory is created."""
        f = tmp_path / "subdir" / "nested" / "file.txt"
        result = write_file(str(f), "nested content")
        assert "File written" in result
        assert f.read_text() == "nested content"


class TestSearchFiles:
    def test_search_files(self, tmp_path):
        """Create temp dir with files, search for pattern, verify results."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass")
        (tmp_path / "src" / "utils.py").write_text("def util(): pass")
        (tmp_path / "src" / "readme.md").write_text("# docs")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "index.md").write_text("# index")

        result = search_files(str(tmp_path), "*.py")
        assert "main.py" in result
        assert "utils.py" in result
        assert "readme.md" not in result

    def test_search_files_no_match(self, tmp_path):
        """Returns 'No files matching' message when nothing matches."""
        result = search_files(str(tmp_path), "*.xyz")
        assert "No files matching" in result


class TestTerminal:
    def test_terminal(self):
        """Run 'echo hello', verify output contains 'hello'."""
        result = run_terminal("echo hello")
        assert "hello" in result

    def test_terminal_timeout(self):
        """Run sleep 5 with timeout=1, verify timeout handling."""
        result = run_terminal("sleep 5", timeout=1)
        assert "timed out" in result.lower()


class TestExecuteTool:
    def test_execute_read_file(self, tmp_path):
        """execute_tool dispatches to the correct function."""
        f = tmp_path / "test.txt"
        f.write_text("tool content")
        result = execute_tool("read_file", ALL_TOOLS, path=str(f))
        assert "tool content" in result

    def test_execute_tool_not_found(self):
        """execute_tool with unknown name returns error."""
        result = execute_tool("nonexistent", ALL_TOOLS)
        assert "Error" in result
        assert "not available" in result


class TestToolRegistries:
    def test_all_tools_has_keys(self):
        assert "read_file" in ALL_TOOLS
        assert "write_file" in ALL_TOOLS
        assert "search_files" in ALL_TOOLS
        assert "terminal" in ALL_TOOLS

    def test_read_only_tools_no_write(self):
        assert "read_file" in READ_ONLY_TOOLS
        assert "write_file" not in READ_ONLY_TOOLS

    def test_write_tools_has_terminal(self):
        assert "terminal" in WRITE_TOOLS

    def test_research_tools_readonly(self):
        assert read_file in RESEARCH_TOOLS.values()
        assert run_terminal not in RESEARCH_TOOLS.values()
