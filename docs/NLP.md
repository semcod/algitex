# NLP — Deterministic Refactor Helpers

Deterministic NLP-based refactoring without LLM calls. Pure code transformations using AST and regex.

## Overview

NLP module provides fast, deterministic code refactoring operations that don't require LLM calls. These are **Tier 0** operations in the three-tier system.

# Fix verbose docstrings
algitex nlp docstrings --dry-run
algitex nlp docstrings --execute

# Optimize and organize imports
algitex nlp imports --execute

# Remove dead code (unused functions, classes)
algitex nlp dead-code --execute

# Find and refactor duplicate code blocks
algitex nlp duplicates --execute
```

### Docstring Shortener

Converts verbose docstrings to concise Google/NumPy style:

```python
# Before
"""
This function takes two arguments, a and b, and returns their sum.
It was written on a sunny day in 2023.
"""
# After
"""Return sum of a and b."""
```

### Import Optimizer

- Sorts imports (stdlib, third-party, local)
- Removes unused imports
- Combines multiple imports from same module
- Groups by PEP 8 conventions

```python
# Before
import os
import sys
from typing import Dict
import os.path
from typing import List

# After
import os
import os.path
import sys
from typing import Dict, List
```

### Dead Code Detector

Finds and removes:
- Unused functions
- Unused classes
- Unreachable code after `return`
- Unused imports

```python
# Detected and removed
def _helper():  # Never called
    pass
```

### Duplicate Finder

Identifies repeated code blocks and suggests extraction:

```python
# Duplicate detected in 3 locations
if user.is_admin:
    log.info("Admin action")
    perform_action()

## Integration with Three-Tier System

NLP operations are **Tier 0** (Algorithmic) in the TODO pipeline:

```python
from algitex.todo import parallel_fix_and_update

# Tier 0: Deterministic NLP fixes
result = parallel_fix_and_update(
    "TODO.md",
    workers=8,
    dry_run=False,
    tasks=nlp_tasks  # unused_import, fstring, etc.
)
```

## Performance

| Operation | Throughput | LLM? |
|-----------|------------|------|
| docstrings | ~500 files/sec | ❌ No |
| imports | ~1000 files/sec | ❌ No |
| dead-code | ~800 files/sec | ❌ No |
| duplicates | ~200 files/sec | ❌ No |

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--execute` | Apply changes | False (dry-run) |
| `--min-lines` | Min duplicate block size | 5 |
| `--style` | Docstring style | google |

## See Also

- [todo.md](./todo.md) — Three-tier TODO fixing system
- [MICROTASK.md](./MICROTASK.md) — Small LLM task pipeline
