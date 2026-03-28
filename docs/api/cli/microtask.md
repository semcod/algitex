# `cli.microtask`

CLI commands for the MicroTask pipeline.

## Public API

```python
__all__ = ['microtask_app', 'microtask_classify', 'microtask_plan', 'microtask_run']
```

## Functions

### `microtask_classify`

```python
def microtask_classify(todo_path: str=typer.Argument('TODO.md', help='Path to a prefact-style TODO file.')) -> None
```

Classify TODO items into atomic MicroTasks.

### `microtask_plan`

```python
def microtask_plan(todo_path: str=typer.Argument('TODO.md', help='Path to a prefact-style TODO file.')) -> None
```

Show execution plan, tiers, and model hints.

### `microtask_run`

```python
def microtask_run(todo_path: str=typer.Argument('TODO.md', help='Path to a prefact-style TODO file.'), algo_only: bool=typer.Option(False, '--algo-only', help='Run only deterministic tasks.'), tier: int | None=typer.Option(None, '--tier', min=0, max=3, help='Run only tasks from a single tier.'), dry_run: bool=typer.Option(True, '--dry-run/--execute', help='Preview changes without writing files.'), workers: int=typer.Option(8, '--workers', min=1, help='Parallel workers for deterministic tasks.'), llm_workers: int=typer.Option(4, '--llm-workers', min=1, help='Parallel workers for small LLM tasks.'), rate_limit: float=typer.Option(10.0, '--rate-limit', min=0.1, help='LLM requests per second.')) -> None
```

Execute the three-phase microtask pipeline.
