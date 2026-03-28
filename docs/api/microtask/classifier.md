# `microtask.classifier`

Classification helpers for prefact TODO lines.

## Public API

```python
__all__ = ['KNOWN_MAGIC_NUMBERS', 'classify_prefact_line', 'classify_todo_file']
```

## Functions

### `classify_prefact_line`

```python
def classify_prefact_line(line: str, task_id: int, base_dir: str | Path | None=None) -> MicroTask | None
```

Convert one prefact-style TODO line into a MicroTask.

### `classify_todo_file`

```python
def classify_todo_file(path: str | Path) -> list[MicroTask]
```

Parse a TODO file and return the MicroTask view.
