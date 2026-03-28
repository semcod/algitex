# `project.autofix`

AutoFix integration mixins for Project class.

## Classes

### `AutoFixMixin`

AutoFix integration functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self, todo_path: str) -> None
```

#### `fix_issues`

```python
def fix_issues(self, limit: Optional[int]=None, backend: str='auto', filter_file: Optional[str]=None) -> dict
```

Fix issues from TODO.md.

#### `fix_issue`

```python
def fix_issue(self, task_id: str, backend: str='auto') -> Optional[dict]
```

Fix a specific issue by task ID.

#### `list_todo_tasks`

```python
def list_todo_tasks(self) -> list
```

List all pending TODO tasks.

#### `sync`

```python
def sync(self) -> dict
```

Sync tickets to external backend.
