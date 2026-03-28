# `tools.autofix.aider_backend`

Aider backend for AutoFix — refactored to reduce cyclomatic complexity.

## Classes

### `AiderBackend`

Fix issues using Aider CLI.

**Methods:**

#### `__init__`

```python
def __init__(self, dry_run: bool=False)
```

#### `fix`

```python
def fix(self, task: Task) -> FixResult
```

Fix a task using Aider — main entry point with reduced CC.
