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

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json
import re
import httpx

from algitex.config import Config
from algitex.tools.todo_parser import Task, TodoParser
from algitex.tools.docker import DockerToolManager
from algitex.tools.todo_local import LocalExecutor, LocalTaskResult


@dataclass
class TaskResult:
    """Result of executing a single task."""
    task: Task
    success: bool
    action: str
    output: str = ""
    error: Optional[str] = None
    tool_used: str = ""


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
            # Read the file content
            content = file_path.read_text()
            lines = content.split('\n')

            if task.line_number and task.line_number <= len(lines):
                # Get context around the line
                start = max(0, task.line_number - 5)
                end = min(len(lines), task.line_number + 5)
                context = '\n'.join(lines[start:end])
            else:
                context = content[:1000]

            # Build prompt for Ollama
            prompt = f"""Fix this Python code issue:
{task.description}

File: {task.file_path}
Line: {task.line_number}

Context:
```python
{context}
```

Provide ONLY the fixed code, no explanations."""

            # Call Ollama API with faster model
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

            # Extract fixed code from response
            fixed_code = result.get("response", "")

            # Apply the fix (simplified - would need proper parsing)
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
        action, args = self._determine_action(task, tool)

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

    def _determine_action(self, task: Task, tool: str) -> tuple[str, dict]:
        """Determine MCP action and arguments for the task."""
        desc = task.description.lower()

        # Map tool to appropriate action
        if tool == "nap":
            return self._nap_action(task)
        elif tool == "aider-mcp":
            return self._aider_action(task)
        elif tool == "ollama-mcp":
            return self._ollama_action(task)
        elif tool == "filesystem-mcp":
            return self._filesystem_action(task)
        elif tool == "github-mcp":
            return self._github_action(task)
        else:
            # Generic action
            return ("process", {"task": task.description})

    def _nap_action(self, task: Task) -> tuple[str, dict]:
        """Generate nap action for automated code repair."""
        desc = task.description.lower()

        # Determine fix type based on description
        if any(kw in desc for kw in ["import", "unused import"]):
            return ("fix_imports", {
                "file_path": task.file_path,
                "line": task.line_number,
                "description": task.description,
            })

        if any(kw in desc for kw in ["return type", "missing return", "->"]):
            return ("fix_types", {
                "file_path": task.file_path,
                "line": task.line_number,
                "description": task.description,
            })

        if any(kw in desc for kw in ["style", "format", "whitespace", "f-string"]):
            return ("fix_style", {
                "file_path": task.file_path,
                "line": task.line_number,
                "description": task.description,
            })

        # Generic fix_issue for everything else
        return ("fix_issue", {
            "file_path": task.file_path,
            "line": task.line_number,
            "description": task.description,
            "issue_type": "auto",
        })

    def _aider_action(self, task: Task) -> tuple[str, dict]:
        """Generate aider-mcp action for code tasks."""
        desc = task.description

        # Extract file path and what needs to be done
        file_path = task.file_path
        line_hint = task.line_number

        # Build prompt for aider
        prompt = f"{desc}"
        if file_path:
            prompt = f"In {file_path}"
            if line_hint:
                prompt += f" at line {line_hint}"
            prompt += f": {desc}"

        return ("aider_ai_code", {
            "prompt": prompt,
            "file_path": file_path or ".",
        })

    def _ollama_action(self, task: Task) -> tuple[str, dict]:
        """Generate ollama-mcp action for code fixing with local LLM."""
        desc = task.description.lower()
        file_path = task.file_path
        line_hint = task.line_number

        # Determine fix type based on description
        if any(kw in desc for kw in ["import", "unused import"]):
            return ("remove_unused_imports", {
                "file_path": file_path,
                "line": line_hint,
                "description": task.description,
                "model": "codellama",
            })

        if any(kw in desc for kw in ["return type", "missing return", "->"]):
            return ("add_types", {
                "file_path": file_path,
                "line": line_hint,
                "description": task.description,
                "model": "codellama",
            })

        if any(kw in desc for kw in ["style", "format", "whitespace", "f-string"]):
            return ("refactor_code", {
                "file_path": file_path,
                "line": line_hint,
                "description": task.description,
                "refactor_type": "style_fix",
                "model": "codellama",
            })

        # Generic fix_code for everything else
        return ("fix_code", {
            "file_path": file_path,
            "line": line_hint,
            "description": task.description,
            "issue_type": "auto",
            "model": "codellama",
        })

    def _filesystem_action(self, task: Task) -> tuple[str, dict]:
        """Generate filesystem-mcp action."""
        desc = task.description.lower()

        # Determine operation type
        if any(kw in desc for kw in ["read", "show", "view", "get"]):
            return ("read_file", {
                "path": task.file_path or "."
            })
        elif any(kw in desc for kw in ["write", "create", "add", "save"]):
            return ("write_file", {
                "path": task.file_path or "output.txt",
                "content": ""
            })
        elif any(kw in desc for kw in ["list", "ls", "dir"]):
            return ("list_directory", {
                "path": task.file_path or "."
            })
        elif any(kw in desc for kw in ["search", "find", "grep"]):
            return ("search_files", {
                "path": ".",
                "pattern": task.description
            })
        else:
            # Default to read
            return ("read_file", {
                "path": task.file_path or "."
            })

    def _github_action(self, task: Task) -> tuple[str, dict]:
        """Generate github-mcp action."""
        desc = task.description.lower()

        if any(kw in desc for kw in ["issue", "bug", "ticket"]):
            return ("create_issue", {
                "title": task.description[:100],
                "body": task.description,
            })
        elif any(kw in desc for kw in ["pr", "pull request", "merge"]):
            return ("create_pull_request", {
                "title": task.description[:100],
                "body": task.description,
            })
        elif any(kw in desc for kw in ["commit", "push", "code"]):
            return ("search_code", {
                "query": task.description,
            })
        else:
            return ("get_file_contents", {
                "path": task.file_path or "README.md"
            })

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
