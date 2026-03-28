# `todo.verifier`

TODO verification - check which prefact tasks are still valid.

Usage:
    from algitex.todo.verifier import TodoVerifier
    verifier = TodoVerifier("TODO.md")
    result = verifier.verify()
    print(f"Open: {result.still_open}, Fixed: {result.already_fixed}")


## Functions

### `verify_todos`

```python
def verify_todos(todo_path: str | Path='TODO.md') -> VerificationResult
```

Quick verification function.

    Args:
        todo_path: Path to TODO.md file

    Returns:
        VerificationResult with counts
    

## Classes

### `TodoTask`

Single TODO task from prefact output.

### `VerificationResult`

Result of TODO verification.

### `TodoVerifier`

Verify which TODO tasks from prefact are still valid.

**Methods:**

#### `__init__`

```python
def __init__(self, todo_path: str | Path)
```

#### `parse`

```python
def parse(self) -> list[TodoTask]
```

Parse TODO.md file into list of tasks.

#### `verify`

```python
def verify(self) -> VerificationResult
```

Verify all tasks and return result.

#### `print_report`

```python
def print_report(self) -> None
```

Print verification report.
