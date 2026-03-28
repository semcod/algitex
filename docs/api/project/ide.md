# `project.ide`

IDE integration mixins for Project class.

## Classes

### `IDEMixin`

IDE integration functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self) -> None
```

#### `setup_ide`

```python
def setup_ide(self, tool_name: str) -> bool
```

Setup IDE tool.

#### `fix_with_claude`

```python
def fix_with_claude(self, file_path: str, instruction: str, model: str='qwen3-coder:latest') -> bool
```

Fix file using Claude Code.

#### `fix_with_aider`

```python
def fix_with_aider(self, file_path: str, instruction: str, model: str='qwen3-coder:latest') -> bool
```

Fix file using Aider.

#### `detect_editor`

```python
def detect_editor(self) -> Optional[str]
```

Detect which editor is available.

#### `get_ide_status`

```python
def get_ide_status(self) -> dict
```

Get status of all IDE tools.
