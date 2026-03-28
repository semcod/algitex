# Example 35: Sprint 3 CC Reduction Patterns

Demonstrates the cyclomatic complexity reduction patterns introduced in Sprint 3.

## What it shows

- **Dict dispatch pattern** (`classify.py`): CC 50 → 4 (92% reduction)
- **Strategy pattern** (`repair.py`): CC 30 → 6 (80% reduction)  
- **Pipeline pattern** (`verify.py`): CC 29 → 5 (83% reduction)
- **Orchestrator pattern** (`fixer.py`): 724L → ~450L (38% reduction)

## Running

```bash
cd examples/35-sprint3-patterns
python main.py
```

## Key patterns demonstrated

1. **Dict Dispatch**: Replace if/elif chains with dictionary lookup
2. **Strategy**: Extract repair logic into separate functions
3. **Pipeline**: Split verification into discrete steps
4. **Orchestrator**: Delegation to specialized modules
