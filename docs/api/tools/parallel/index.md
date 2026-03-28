# `tools.parallel`

Parallel task coordination for algitex — region-based conflict-free execution.

This package provides tools for parallel execution of refactoring tasks
using git worktrees and AST-based region locking to prevent conflicts.

Exports:
    - RegionType, CodeRegion, TaskAssignment, MergeResult (data models)
    - RegionExtractor (AST-based region extraction)
    - TaskPartitioner (conflict-free task partitioning)
    - ParallelExecutor (worktree-based execution)

Example:
    from algitex.tools.parallel import ParallelExecutor

    executor = ParallelExecutor("/path/to/project", max_agents=4)
    results = executor.execute(tickets, tool="aider-mcp")


## Public API

```python
__all__ = ['RegionType', 'CodeRegion', 'TaskAssignment', 'MergeResult', 'RegionExtractor', 'TaskPartitioner', 'ParallelExecutor']
```
