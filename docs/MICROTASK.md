# MicroTask — Atomic Tasks for Small LLMs

Pipeline for breaking down and executing atomic micro-tasks optimized for small LLMs (7B parameters).

## Overview

MicroTask decomposes complex refactoring tasks into small, atomic units that can be processed efficiently by local LLMs like `qwen2.5-coder:7b` or `codellama:7b`.

## CLI Commands

```bash
# Classify tasks by complexity
algitex microtask classify

# Generate execution plan
algitex microtask plan

# Execute micro-tasks
algitex microtask run --workers 4
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MicroTask Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. classify → Categorize tasks (Simple/Complex/Atomic)    │
│  2. plan    → Generate execution strategy                  │
│  3. run     → Three-phase execution:                     │
│               - Extract context                            │
│               - Generate fix                               │
│               - Validate & apply                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Task Types

| Type | Description | Example |
|------|-------------|---------|
| `SIMPLE` | Single-line changes | Rename variable |
| `ATOMIC` | Self-contained function | Add type hints |
| `COMPLEX` | Multi-file coordination | Extract interface |

## Context Extraction

MicroTask automatically extracts minimal context needed for the LLM:

- **Function snippet** (not full file)
- **Imports** relevant to the function
- **Call sites** (where function is used)
- **Type hints** if available

This keeps token count low (< 2K tokens) for fast 7B model inference.

## Integration with Three-Tier System

MicroTask is used in **Tier 1** (Small LLM) of the TODO fixing pipeline:

```python
from algitex.todo import MicroFixer

micro_fixer = MicroFixer(
    ollama_url="http://localhost:11434",
    model="qwen2.5-coder:7b",
    workers=4,
    dry_run=False,
)

# Fix micro-tasks (Tier 1)
result = micro_fixer.fix_tasks(micro_tasks)
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--workers` | Parallel workers | 4 |
| `--model` | Ollama model | qwen2.5-coder:7b |
| `--dry-run` | Preview changes | True |
| `--context-lines` | Lines of context | 5 |

## See Also

- [todo.md](./todo.md) — Three-tier TODO fixing system
- [BATCHFIX.md](./BATCHFIX.md) — Batch processing with grouping
