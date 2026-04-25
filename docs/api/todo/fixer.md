# `todo.fixer`

Parallel auto-fixer for prefact TODO tasks — Orchestrator only.

Groups tasks by file, fixes each file independently in parallel.
No merge conflicts because each worker touches a different file.

Usage:
    from algitex.todo.fixer import parallel_fix
    parallel_fix("TODO.md", workers=8, dry_run=True)


## Public API

```python
__all__ = ['TodoTask', 'FixResult', 'parse_todo', 'fix_file', 'parallel_fix', 'parallel_fix_and_update', 'mark_tasks_completed', 'FIXERS']
```

### `parse_todo`

```python
def parse_todo(todo_path: str | Path) -> list[TodoTask]
```

Parse TODO.md → list of tasks, filtering worktree duplicates.

### `fix_file`

```python
def fix_file(file_path: str, tasks: list[TodoTask], dry_run: bool=True) -> FixResult
```

Fix all tasks in a single file using strategy dispatch.
    
    CC: 6 (dispatcher + loop + 4 category handlers)
    

### `parallel_fix`

```python
def parallel_fix(todo_path: str | Path, workers: int=8, dry_run: bool=True, category_filter: str | None=None, categories: set[str] | None=None, tasks: list[TodoTask] | None=None) -> dict[str, int]
```

Fix all TODO tasks in parallel, one worker per file.

### `mark_tasks_completed`

```python
def mark_tasks_completed(todo_path: str | Path, completed_tasks: list[TodoTask]) -> int
```

Mark completed tasks in TODO.md by changing - [ ] to - [x].

### `FixResult`

Result of fixing a file.
