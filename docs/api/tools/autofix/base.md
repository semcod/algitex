# `tools.autofix.base`

Base classes and utilities for AutoFix.

## Classes

### `FixResult`

Result of fixing an issue.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary.

### `Task`

Minimal task representation for backends.

### `AutoFixBackend`

Base class for autofix backends.

**Methods:**

#### `fix`

```python
def fix(self, task: Task) -> FixResult
```

Fix a task. Override in subclass.
