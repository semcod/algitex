# `todo.verify`

TODO verification pipeline — check tasks against actual code state.

Splits todo_verify_prefact into 4-step pipeline:
1. _run_prefact_scan() → raw_issues
2. _parse_todo_file() → existing_tasks
3. _diff_issues() → VerifyResult
4. _format_verify_report() → str


## Public API

```python
__all__ = ['VerifyResult', 'TodoTask', 'verify_todos', 'prune_outdated_tasks', '_format_verify_report']
```

### `verify_todos`

```python
def verify_todos(todo_path: str='TODO.md', project_path: str='.') -> VerifyResult
```

Pipeline: scan → parse → diff → result.
    
    CC: 5 (4 pipeline steps + 1 orchestrator)
    

### `VerifyResult`

Result of TODO verification.

### `TodoTask`

Single TODO task entry.
