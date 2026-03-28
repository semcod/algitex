# `microtask.slicer`

Context slicing helpers for MicroTask prompts.

## Public API

```python
__all__ = ['ContextSlicer']
```

## Classes

### `ContextSlicer`

Extract the smallest useful context for a micro task.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str | Path='.') -> None
```

#### `slice`

```python
def slice(self, task: MicroTask) -> MicroTask
```

Populate context fields on a task and return it.
