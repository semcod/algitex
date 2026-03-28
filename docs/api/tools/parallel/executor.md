# `tools.parallel.executor`

Parallel execution — execute tickets using git worktrees with region locking.

## Classes

### `ParallelExecutor`

Execute tickets in parallel using git worktrees + region locking.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str, max_agents: int=4)
```

#### `execute`

```python
def execute(self, tickets: List[Dict], tool: str='aider-mcp') -> List[MergeResult]
```

Full parallel execution pipeline.
