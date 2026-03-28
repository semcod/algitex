"""Todo executor — execute parsed tasks via Docker MCP tools.

Usage:
    from algitex.tools.todo_executor import TodoExecutor
    from algitex.tools.todo_parser import TodoParser

    parser = TodoParser("TODO.md")
    tasks = parser.parse()

    executor = TodoExecutor(".")
    results = executor.run(tasks, tool_name="filesystem-mcp")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import re

from algitex.config import Config
from algitex.tools.todo_parser import Task
from algitex.tools.docker import DockerToolManager


@dataclass
class TaskResult:
    """Result of executing a single task."""
    task: Task
    success: bool
    action: str  # What MCP action was taken
    output: str = ""
    error: Optional[str] = None
    tool_used: str = ""
    cost_usd: float = 0.0


class TodoExecutor:
    """Execute todo tasks using Docker MCP tools."""

    def __init__(self, project_path: str = ".", config: Optional[Config] = None):
        self.project_path = Path(project_path).resolve()
        self.config = config or Config.load()
        self.docker = DockerToolManager(self.config)
        self._results: list[TaskResult] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.docker.__exit__(exc_type, exc_val, exc_tb)

    def run(
        self,
        tasks: list[Task],
        tool_name: str = "filesystem-mcp",
        dry_run: bool = False,
    ) -> list[TaskResult]:
        """Execute all tasks using the specified Docker MCP tool."""
        self._results = []

        for task in tasks:
            result = self._execute_task(task, tool_name, dry_run)
            self._results.append(result)

        return self._results

    def _execute_task(
        self,
        task: Task,
        tool_name: str,
        dry_run: bool,
    ) -> TaskResult:
        """Execute a single task via MCP."""
        if dry_run:
            return TaskResult(
                task=task,
                success=True,
                action="dry_run",
                output=f"Would execute: {task.description}",
                tool_used=tool_name,
            )

        # Parse task description to determine action
        action, args = self._parse_action(task)

        try:
            # Ensure tool is running
            if tool_name not in self.docker.list_running():
                self.docker.spawn(tool_name)

            # Call the appropriate MCP tool
            result = self.docker.call_tool(tool_name, action, args)

            # Check for errors in result
            if "error" in result:
                return TaskResult(
                    task=task,
                    success=False,
                    action=action,
                    error=str(result.get("error", "Unknown error")),
                    tool_used=tool_name,
                )

            # Extract output from MCP result
            output = self._extract_output(result)

            return TaskResult(
                task=task,
                success=True,
                action=action,
                output=output,
                tool_used=tool_name,
            )

        except Exception as e:
            return TaskResult(
                task=task,
                success=False,
                action=action,
                error=str(e),
                tool_used=tool_name,
            )

    def _parse_action(self, task: Task) -> tuple[str, dict]:
        """Parse task description to determine MCP action and arguments."""
        desc = task.description.lower()

        # File operations
        if any(kw in desc for kw in ["fix", "repair", "correct", "update", "change"]):
            if task.file_path:
                return self._parse_fix_action(task)

        if any(kw in desc for kw in ["add", "create", "insert"]):
            return self._parse_create_action(task)

        if any(kw in desc for kw in ["remove", "delete", "drop"]):
            return self._parse_delete_action(task)

        if any(kw in desc for kw in ["read", "show", "display", "get", "view"]):
            return self._parse_read_action(task)

        # Analysis operations
        if any(kw in desc for kw in ["analyze", "check", "validate", "test"]):
            return ("analyze", {"target": task.file_path or "."})

        # Default: try to read/understand the context
        return self._parse_read_action(task)

    def _parse_fix_action(self, task: Task) -> tuple[str, dict]:
        """Parse a fix/correction task."""
        desc = task.description

        # Try to extract what needs to be fixed
        # Pattern: "Fix X in file.py" or "Function X missing Y"
        fix_patterns = [
            r'(?:fix|repair|correct|add|update)\s+(.+?)(?:\s+in\s+|\s+at\s+|\s*[:\-]\s*)',
            r'(?:missing|needs?|requires?)\s+(.+?)(?:\s+in\s+|\s+for\s+)',
        ]

        what_to_fix = None
        for pattern in fix_patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                what_to_fix = match.group(1).strip()
                break

        if task.file_path:
            target_file = str(self.project_path / task.file_path)
        else:
            target_file = str(self.project_path)

        return ("edit", {
            "path": target_file,
            "line": task.line_number,
            "description": what_to_fix or desc,
            "original": None,
            "replacement": None,
        })

    def _parse_create_action(self, task: Task) -> tuple[str, dict]:
        """Parse a create/add task."""
        # Extract file path if mentioned
        file_match = re.search(r'(?:file|path)\s+["\']?(\S+)["\']?', task.description, re.IGNORECASE)
        target_file = file_match.group(1) if file_match else (task.file_path or "new_file.txt")

        return ("create", {
            "path": str(self.project_path / target_file),
            "content": "",
        })

    def _parse_delete_action(self, task: Task) -> tuple[str, dict]:
        """Parse a remove/delete task."""
        if task.file_path:
            return ("delete", {"path": str(self.project_path / task.file_path)})
        return ("delete", {"path": str(self.project_path)})

    def _parse_read_action(self, task: Task) -> tuple[str, dict]:
        """Parse a read/view task."""
        if task.file_path:
            target = str(self.project_path / task.file_path)
            return ("read", {"path": target, "offset": task.line_number, "limit": 50})
        return ("list", {"path": str(self.project_path)})

    def _extract_output(self, result: dict) -> str:
        """Extract meaningful output from MCP result."""
        # Handle different response formats
        if "result" in result:
            result_data = result["result"]
            if isinstance(result_data, dict):
                # Look for content in various fields
                for key in ["content", "text", "output", "data", "result"]:
                    if key in result_data:
                        value = result_data[key]
                        if isinstance(value, list):
                            return "\n".join(str(item) for item in value)
                        return str(value)
            return str(result_data)

        if "content" in result:
            content = result["content"]
            if isinstance(content, list):
                return "\n".join(str(item) for item in content)
            return str(content)

        return json.dumps(result, indent=2)

    def get_summary(self) -> dict:
        """Get execution summary."""
        if not self._results:
            return {"total": 0, "success": 0, "failed": 0}

        success = sum(1 for r in self._results if r.success)
        failed = sum(1 for r in self._results if not r.success)

        return {
            "total": len(self._results),
            "success": success,
            "failed": failed,
            "success_rate": success / len(self._results) if self._results else 0,
        }
