# `microtask.executor`

Three-phase MicroTask executor.

## Public API

```python
__all__ = ['MicroTaskExecutor', 'PhaseResult']
```

## Classes

### `PhaseResult`

Summary for a single execution phase.

**Methods:**

#### `throughput`

```python
def throughput(self) -> float
```

Return tasks per second for the phase.

#### `as_dict`

```python
def as_dict(self) -> dict[str, int | float | str | list[str]]
```

### `MicroTaskExecutor`

Execute micro tasks in three tiers: algorithmic, small LLM, big LLM.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str | Path='.', ollama_url: str='http://localhost:11434', algo_workers: int=8, llm_workers: int=4, rate_limit_rps: float=10.0) -> None
```

#### `execute`

```python
def execute(self, tasks: list[MicroTask], dry_run: bool=True) -> list[PhaseResult]
```

Run all micro tasks in the three execution phases.

#### `group_by_file`

```python
def group_by_file(self, tasks: list[MicroTask]) -> dict[str, MicroTaskBatch]
```

Return file-grouped batches for planning or execution.

#### `close`

```python
def close(self) -> None
```

Close the shared Ollama client.
