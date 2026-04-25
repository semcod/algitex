"""Todo runner — execute todo tasks via Docker MCP tools.

Integrates with MCP tools defined in docker-tools.yaml:
- aider-mcp: AI code editing
- filesystem-mcp: File read/write operations
- github-mcp: GitHub operations
- ollama-mcp: Local LLM code fixing

Usage:
    from algitex.tools.todo_runner import TodoRunner, Task

    runner = TodoRunner(".")
    results = runner.run_from_file("TODO.md", tool="ollama-mcp")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import httpx

from algitex.config import Config
from algitex.tools.todo_parser import Task, TodoParser
from algitex.tools.docker import DockerToolManager
from algitex.tools.todo_local import LocalExecutor
from algitex.tools.todo_actions import determine_action
from algitex.tools.todo_executor import TaskResult


class TodoRunner:
    """Execute todo tasks using Docker MCP tools with local fallback."""

    def __init__(self, project_path: str = ".", config: Optional[Config] = None):
        self.project_path = Path(project_path).resolve()
        self.config = config or Config.load()
        self.docker = DockerToolManager(self.config)
        self.local = LocalExecutor(project_path)
        self._results: list[TaskResult] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.docker.__exit__(exc_type, exc_val, exc_tb)

    def run_from_file(
        self,
        todo_file: str,
        tool: str = "aider-mcp",
        dry_run: bool = False,
        limit: int = 0,
    ) -> list[TaskResult]:
        """Parse todo file and execute all pending tasks."""
        parser = TodoParser(todo_file)
        tasks = parser.parse()

        if not tasks:
            return []

        if limit > 0:
            tasks = tasks[:limit]

        return self.run(tasks, tool=tool, dry_run=dry_run)

    def run(
        self,
        tasks: list[Task],
        tool: str = "local",
        dry_run: bool = False,
    ) -> list[TaskResult]:
        """Execute tasks using specified tool or local fallback."""
        self._results = []

        # If using local tool, skip Docker entirely
        if tool == "local":
            for task in tasks:
                result = self._execute_local(task, dry_run)
                self._results.append(result)
            return self._results

        # Special handling for ollama-mcp - use direct API
        if tool == "ollama-mcp":
            for task in tasks:
                result = self._execute_ollama(task, dry_run)
                self._results.append(result)
            return self._results

        # Ensure Docker tool is running
        if tool not in self.docker.list_running():
            try:
                self.docker.spawn(tool)
            except Exception as e:
                # Fall back to local execution for all tasks
                for task in tasks:
                    result = self._execute_local(task, dry_run)
                    self._results.append(result)
                return self._results

        for task in tasks:
            result = self._execute_task(task, tool, dry_run)
            self._results.append(result)

        return self._results

    def _execute_local(self, task: Task, dry_run: bool) -> TaskResult:
        """Execute task using local executor."""
        if dry_run:
            return TaskResult(
                task=task,
                success=True,
                action="dry_run",
                output=f"Would execute locally: {task.description}",
                tool_used="local",
            )

        if not self.local.can_execute(task):
            return TaskResult(
                task=task,
                success=False,
                action="skip",
                error="No local fix available for this task (requires Docker MCP)",
                tool_used="local",
            )

        local_result = self.local.execute(task)
        return TaskResult(
            task=task,
            success=local_result.success,
            action=f"local_{local_result.action}",
            output=local_result.output,
            error=local_result.error,
            tool_used="local",
        )

    def _execute_ollama(self, task: Task, dry_run: bool) -> TaskResult:
        """Execute task using Ollama local LLM API."""
        if dry_run:
            return TaskResult(
                task=task,
                success=True,
                action="dry_run",
                output=f"Would fix with Ollama LLM: {task.description}",
                tool_used="ollama-mcp",
            )

        if not task.file_path:
            return TaskResult(
                task=task,
                success=False,
                action="skip",
                error="No file path for Ollama fix",
                tool_used="ollama-mcp",
            )

        file_path = self.project_path / task.file_path
        if not file_path.exists():
            return TaskResult(
                task=task,
                success=False,
                action="skip",
                error=f"File not found: {file_path}",
                tool_used="ollama-mcp",
            )

        try:
            prompt = self._build_ollama_prompt(task, file_path)
            fixed_code = self._call_ollama_api(prompt)

            if fixed_code and len(fixed_code) > 10:
                return TaskResult(
                    task=task,
                    success=True,
                    action="ollama_fix",
                    output=f"Ollama suggested fix for {task.file_path}",
                    tool_used="ollama-mcp",
                )
            else:
                return TaskResult(
                    task=task,
                    success=False,
                    action="ollama_fix",
                    error="Ollama returned empty or invalid response",
                    tool_used="ollama-mcp",
                )

        except Exception as e:
            return TaskResult(
                task=task,
                success=False,
                action="ollama_error",
                error=f"Ollama API error: {str(e)}",
                tool_used="ollama-mcp",
            )

    def _build_ollama_prompt(self, task: Task, file_path: Path) -> str:
        """Build a fix prompt with file context for Ollama."""
        content = file_path.read_text()
        lines = content.split('\n')

        if task.line_number and task.line_number <= len(lines):
            start = max(0, task.line_number - 5)
            end = min(len(lines), task.line_number + 5)
            context = '\n'.join(lines[start:end])
        else:
            context = content[:1000]

        return f"""Fix this Python code issue:
{task.description}

File: {task.file_path}
Line: {task.line_number}

Context:
```python
{context}
```

Provide ONLY the fixed code, no explanations."""

    def _call_ollama_api(self, prompt: str) -> str:
        """Call Ollama generate API and return the response text."""
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 500,
                }
            },
            timeout=120.0,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")

    def _execute_task(
        self,
        task: Task,
        tool: str,
        dry_run: bool,
    ) -> TaskResult:
        """Execute single task via appropriate MCP action."""
        if dry_run:
            return TaskResult(
                task=task,
                success=True,
                action="dry_run",
                output=f"Would execute: {task.description}",
                tool_used=tool,
            )

        # Determine best action based on task description
        action, args = determine_action(task, tool)

        try:
            result = self.docker.call_tool(tool, action, args)

            if "error" in result:
                # Try local execution as fallback
                if self.local.can_execute(task):
                    local_result = self.local.execute(task)
                    return TaskResult(
                        task=task,
                        success=local_result.success,
                        action=f"local_{local_result.action}",
                        output=local_result.output,
                        error=local_result.error,
                        tool_used="local",
                    )
                return TaskResult(
                    task=task,
                    success=False,
                    action=action,
                    error=str(result.get("error", "Unknown error")),
                    tool_used=tool,
                )

            output = self._format_output(result)

            return TaskResult(
                task=task,
                success=True,
                action=action,
                output=output,
                tool_used=tool,
            )

        except Exception as e:
            # Try local execution as fallback
            if self.local.can_execute(task):
                local_result = self.local.execute(task)
                return TaskResult(
                    task=task,
                    success=local_result.success,
                    action=f"local_{local_result.action}",
                    output=local_result.output,
                    error=local_result.error,
                    tool_used="local",
                )
            return TaskResult(
                task=task,
                success=False,
                action=action,
                error=str(e),
                tool_used=tool,
            )

    def _format_output(self, result: dict) -> str:
        """Extract meaningful output from MCP result."""
        if "result" in result:
            result_data = result["result"]
            if isinstance(result_data, dict):
                for key in ["content", "text", "output", "data", "result", "message"]:
                    if key in result_data:
                        value = result_data[key]
                        if isinstance(value, list):
                            return "\n".join(str(item) for item in value[:10])
                        return str(value)[:500]
            return str(result_data)[:500]

        if "content" in result:
            content = result["content"]
            if isinstance(content, list):
                texts = []
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        texts.append(item["text"])
                return "\n".join(texts)[:500] if texts else str(content)[:500]
            return str(content)[:500]

        return json.dumps(result, indent=2)[:500]

    def get_summary(self) -> dict:
        """Get execution summary."""
        if not self._results:
            return {"total": 0, "success": 0, "failed": 0}

        success = sum(1 for r in self._results if r.success)
        failed = len(self._results) - success

        return {
            "total": len(self._results),
            "success": success,
            "failed": failed,
            "success_rate": success / len(self._results) if self._results else 0,
        }


# Backward compatibility exports
__all__ = ["TodoRunner", "TaskResult"]
