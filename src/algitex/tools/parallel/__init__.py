"""Parallel task coordination for algitex — region-based conflict-free execution.

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
"""
from algitex.tools.parallel.models import (
    CodeRegion,
    MergeResult,
    RegionType,
    TaskAssignment,
)
from algitex.tools.parallel.extractor import RegionExtractor
from algitex.tools.parallel.partitioner import TaskPartitioner
from algitex.tools.parallel.executor import ParallelExecutor

__all__ = [
    # Models
    "RegionType",
    "CodeRegion",
    "TaskAssignment",
    "MergeResult",
    # Components
    "RegionExtractor",
    "TaskPartitioner",
    "ParallelExecutor",
]
