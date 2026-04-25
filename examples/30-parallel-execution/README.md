# Parallel Execution with Region-Based Coordination

```bash
cd examples/30-parallel-execution
```

This example demonstrates algitex's parallel execution capabilities using AST-level region locking to prevent merge conflicts when multiple LLM agents work on the same codebase.

## Key Concepts

- **Region-Based Locking**: Lock functions/classes instead of entire files
- **Git Worktree Isolation**: Each agent works in a separate worktree
- **Semantic Merge Detection**: Line-range overlap analysis
- **Conflict-Free Parallelism**: Intelligent task distribution

## Files

- `main.py` - Main demonstration script
- `parallel_refactoring.py` - Refactoring independent hotspots
- `parallel_multi_tool.py` - Multi-tool parallel execution
- `parallel_real_world.py` - Real-world scenario
- `Makefile` - Build and run commands

## What It Does

1. Analyzes codebase to extract AST regions
2. Partitions tickets into non-conflicting groups
3. Creates git worktrees for each agent
4. Executes agents in parallel
5. Merges results with conflict detection

## Example Output

```
Found 4 open tickets
Extracted 25 AST regions from 8 files

Partition plan (4 tickets → 3 agents):

Agent 0:
  PLF-001: Split Project.status → src/algitex/project/__init__.py
  PLF-004: Lazy init Project.__init__ → src/algitex/project/__init__.py

Agent 1:
  PLF-002: Split BatchProcessor.process → src/algitex/tools/batch.py

Agent 2:
  PLF-003: Extract StdioTransport → src/algitex/tools/docker_transport.py

Executing with 3 parallel agents...

✓ Agent 0: clean [PLF-001, PLF-004]
✓ Agent 1: clean [PLF-002]
✓ Agent 2: clean [PLF-003]
```
