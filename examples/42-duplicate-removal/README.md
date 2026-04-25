# Example 42: Duplicate Code Detection and Removal

Demonstrates how algitex detects and helps eliminate duplicate code using the redup tool and automated refactoring strategies.

## Running

```bash
cd examples/42-duplicate-removal
make run
```

## Overview

Duplicate code is one of the most expensive technical debts:
- Bug fixes must be applied multiple times
- Tests must cover multiple implementations
- Reviewers may miss inconsistent fixes
- Code base bloats unnecessarily

## Detection with redup

```bash
# Scan for duplicates
redup ./src --min-lines 5 --similarity 0.8

# CI integration
redup ./src --min-lines 5 --fail-on-new
```

## Extraction Strategies

| Type | Strategy | When to Use |
|------|----------|-------------|
| Exact Duplicates | Extract to utility function | 100% identical code |
| Near Duplicates | Extract with parameters | Same logic, different data |
| Structural Duplicates | Abstract into class/strategy | Same pattern, different types |
| Cross-file Duplicates | Create shared module | Duplicates across packages |

## algitex Integration

**Analysis phase:**
```bash
algitex analyze  # Generates project/duplication.toon.yaml
```

**Automated fixing:**
```bash
algitex todo fix-auto --category duplicate-code
```

**LLM-assisted for complex cases:**
```bash
algitex todo run --category duplicate-code --tool ollama-mcp
```

## Prevention

1. **CI/CD**: Run redup on every PR
2. **Pre-commit**: Check for duplicates before commit
3. **Team practices**: Check existing utilities first
4. **Architecture**: Clear module boundaries

## ROI Metrics

- Automated fixing: ~600 lines/hour
- Bug prevention: ~5 bugs/year from inconsistent fixes
- Maintenance reduction: 30% less code to maintain

## Files

- `main.py` - Demonstration of duplicate detection and removal
- `Makefile` - Standard run/test/clean targets
