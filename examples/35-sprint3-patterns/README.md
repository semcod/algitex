# Example 35: Sprint 3 CC Reduction Patterns

Demonstrates the cyclomatic complexity reduction patterns introduced in Sprint 3 refactoring.

## Overview

This example showcases four key refactoring patterns that reduced complexity across the algitex codebase:

| Pattern | Module | Before | After | Reduction |
|---------|--------|--------|-------|-----------|
| Dict Dispatch | `classify.py` | CC 50 | CC 4 | 92% |
| Strategy | `repair.py` | CC 30 | CC 6 | 80% |
| Pipeline | `verify.py` | CC 29 | CC 5 | 83% |
| Orchestrator | `fixer.py` | 724L | ~450L | 38% |

## Running

```bash
cd examples/35-sprint3-patterns
make run
```

## Patterns Explained

### 1. Dict Dispatch Pattern

Replaces long if/elif chains with dictionary lookup:

```python
# Before: CC 50
if "unused import" in msg:
    return "unused_import"
elif "return type" in msg:
    return "return_type"
# ... 20+ more

# After: CC 4
from algitex.todo.classify import classify_message
result = classify_message(msg)  # Uses dict dispatch internally
```

### 2. Strategy Pattern

Extracts repair logic into separate functions registered by category:

```python
from algitex.todo.repair import REPAIRERS

# Each category has its own strategy
repair_func = REPAIRERS.get(category)
if repair_func:
    result = repair_func(task, content)
```

### 3. Pipeline Pattern

Splits complex verification into discrete steps:

```python
from algitex.todo.verify import verify_todos

# Internally uses 5-step pipeline:
# 1. _run_prefact_scan()
# 2. _parse_todo_file()
# 3. _diff_issues()
# 4. _validate_task_against_file()
# 5. _format_verify_report()
```

### 4. Orchestrator Pattern

God module becomes thin orchestrator delegating to specialists:

```python
# Before: fixer.py had everything (724 lines)
# After: fixer.py coordinates only (~450 lines)

from algitex.todo import classify_message  # from classify.py
from algitex.todo import REPAIRERS         # from repair.py
from algitex.todo import verify_todos      # from verify.py
```

## Key Takeaways

1. **Dict dispatch** eliminates if/elif chains for categorical logic
2. **Strategy pattern** isolates repair algorithms for easy testing
3. **Pipeline pattern** makes verification steps explicit and composable
4. **Orchestrator pattern** prevents god modules by delegating responsibilities

## Files

- `main.py` - Demonstration of all four patterns
- `Makefile` - Standard run/test/clean targets
