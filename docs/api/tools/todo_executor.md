# `tools.todo_executor`

Todo executor — execute parsed tasks via Docker MCP tools.

Usage:
    from algitex.tools.todo_executor import TodoExecutor
    from algitex.tools.todo_parser import TodoParser

    parser = TodoParser("TODO.md")
    tasks = parser.parse()

    executor = TodoExecutor(".")
    results = executor.run(tasks, tool_name="filesystem-mcp")


### `TaskResult`

Result of executing a single task.

### `TodoExecutor`

Execute todo tasks using Docker MCP tools.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.', config: Optional[Config]=None)
```

#### `run`

```python
def run(self, tasks: list[Task], tool_name: str='filesystem-mcp', dry_run: bool=False) -> list[TaskResult]
```

Execute all tasks using the specified Docker MCP tool.

#### `get_summary`

```python
def get_summary(self) -> dict
```

Get execution summary.
