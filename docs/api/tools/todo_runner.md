# `tools.todo_runner`

Todo runner — execute todo tasks via Docker MCP tools.

Integrates with MCP tools defined in docker-tools.yaml:
- aider-mcp: AI code editing
- filesystem-mcp: File read/write operations
- github-mcp: GitHub operations
- ollama-mcp: Local LLM code fixing

Usage:
    from algitex.tools.todo_runner import TodoRunner, Task

    runner = TodoRunner(".")
    results = runner.run_from_file("TODO.md", tool="ollama-mcp")


## Public API

```python
__all__ = ['TodoRunner', 'TaskResult']
```

### `TaskResult`

Result of executing a single task.

### `TodoRunner`

Execute todo tasks using Docker MCP tools with local fallback.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.', config: Optional[Config]=None)
```

#### `run_from_file`

```python
def run_from_file(self, todo_file: str, tool: str='aider-mcp', dry_run: bool=False, limit: int=0) -> list[TaskResult]
```

Parse todo file and execute all pending tasks.

#### `run`

```python
def run(self, tasks: list[Task], tool: str='local', dry_run: bool=False) -> list[TaskResult]
```

Execute tasks using specified tool or local fallback.

#### `get_summary`

```python
def get_summary(self) -> dict
```

Get execution summary.
