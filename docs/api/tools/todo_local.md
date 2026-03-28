# `tools.todo_local`

Local todo executor - execute simple code fixes without Docker.

Handles common prefact-style fixes:
- Add return type annotations (-> None)
- Remove unused imports
- Convert string concatenation to f-strings
- Add module execution blocks


## Classes

### `LocalTaskResult`

Result of executing a single task locally.

### `LocalExecutor`

Execute simple code fixes locally without Docker.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.')
```

#### `can_execute`

```python
def can_execute(self, task: Task) -> bool
```

Check if task can be executed locally.

#### `execute`

```python
def execute(self, task: Task) -> LocalTaskResult
```

Execute a single task locally.
