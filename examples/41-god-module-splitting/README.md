# Example 41: God Module Splitting

Demonstrates how to split large "god modules" into focused submodules while preserving backward compatibility through re-exports.

## Overview

This example mirrors the real-world refactoring of algitex's own modules:
- `src/algitex/cli/todo.py` (1159L → split into classify, repair, verify, hybrid)
- `src/algitex/todo/fixer.py` (724L → orchestrator only)

## Running

```bash
cd examples/41-god-module-splitting
make run
```

## Key Concepts

### 1. The God Module Problem

A god module mixes multiple concerns in one file:
- Parsing logic
- Classification logic
- Repair logic
- Verification logic
- Orchestration logic

This creates:
- High cyclomatic complexity (CC=50+)
- Merge conflicts (everyone touches one file)
- Tight coupling (hard to test in isolation)
- Navigation difficulty

### 2. Splitting Strategy

**Step 1: Identify cohesive groups**
- Parsing → `todo_parser.py`
- Classification → `classify.py`
- Repair → `repair.py`
- Verification → `verify.py`
- Orchestration → `fixer.py` (thin)

**Step 2: Extract each group**
- Move code verbatim first
- Fix imports afterward

**Step 3: Create thin orchestrator**
- Only coordinates, doesn't implement

**Step 4: Preserve backward compatibility**
- `__init__.py` re-exports everything
- Old imports still work

### 3. Real Metrics from algitex

| Module | CC Change | Pattern | Reduction |
|--------|-----------|---------|-----------|
| `todo/classify.py` | 50 → 4 | Dict dispatch | 92% |
| `todo/repair.py` | 30 → 6 | Strategy | 80% |
| `todo/verify.py` | 29 → 5 | Pipeline | 83% |
| `todo/fixer.py` | 724L → 450L | Orchestrator | 38% |
| `microtask/executor.py` | 27 → 5 | Dispatch table | 81% |
| `tools/batch_logger.py` | 22 → 2 | Split function | 91% |

## Files

- `main.py` - Demonstration of god module splitting concepts
- `Makefile` - Standard run/test/clean targets
