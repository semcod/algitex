# `todo`

TODO management - verification and auto-fixing of prefact tasks.

This module provides tools to manage prefact TODO output:
- verify: Check which tasks are still valid vs already fixed
- fix: Auto-fix mechanical issues (unused imports, return types) in parallel
- benchmark: Measure performance of fix operations

Usage:
    from algitex.todo import verify_todos, fix_todos, benchmark_fix, compare_modes

    # Verify which tasks are still open
    result = verify_todos("TODO.md")
    print(f"Still open: {result.still_open}")

    # Fix mechanical issues in parallel
    stats = fix_todos("TODO.md", workers=8, dry_run=False)
    print(f"Fixed: {stats['fixed']}")

    # Benchmark performance
    result = benchmark_fix("TODO.md", limit=100, workers=8)
    result.print_report()

CLI via algitex:
    algitex todo verify              # verify which tasks are valid
    algitex todo fix --workers 8     # dry-run fix
    algitex todo fix --execute       # apply fixes
    algitex todo fix --category unused_import


## Public API

```python
__all__ = ['TodoVerifier', 'verify_todos', 'VerificationResult', 'parallel_fix', 'fix_todos', 'parse_todo', 'TodoTask', 'REPAIRERS', 'FIXERS', 'mark_tasks_completed', 'parallel_fix_and_update', 'ALGO_CATEGORIES', 'MICRO_CATEGORIES', 'BIG_CATEGORIES', 'KNOWN_MAGIC_CONSTANTS', 'TaskTriage', 'TierSummary', 'classify_message', 'classify_task', 'filter_tasks', 'load_todo_tasks', 'partition_tasks', 'summarise_tasks', 'summarize_tasks', 'FunctionExtractor', 'FunctionSnippet', 'MicroFixResult', 'MicroFixer', 'benchmark_fix', 'benchmark_sequential', 'benchmark_parallel', 'compare_modes', 'BenchmarkResult', 'HybridAutofix', 'HybridResult', 'RateLimiter']
```

### `fix_todos`

```python
def fix_todos(todo_path: str='TODO.md', workers: int=8, dry_run: bool=True, category: str | None=None, categories: set[str] | None=None, tasks: list[TodoTask] | None=None) -> dict[str, int]
```

Convenience wrapper for parallel_fix.

    Args:
        todo_path: Path to TODO.md
        workers: Number of parallel workers
        dry_run: If True, only preview changes
        category: Filter to specific category
        categories: Optional set of categories to include
        tasks: Optional pre-parsed task list to use

    Returns:
        Dict with fixed, skipped, errors counts
    
