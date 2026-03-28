# Example 39: Microtask Pipeline

Demonstrates the microtask classification, planning, and execution pipeline.

## What it shows

- Task decomposition into atomic units
- Context window estimation
- Batching strategy
- Three-phase execution

## Running

```bash
cd examples/39-microtask-pipeline
python main.py
```

## CLI Commands

```bash
# Classify tasks
algitex microtask classify TODO.md

# Plan execution
algitex microtask plan TODO.md --output plan.json

# Run execution
algitex microtask run TODO.md --execute
```
