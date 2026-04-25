# Example 43: Code Health Monitoring

Demonstrates continuous monitoring of code health metrics using algitex analysis pipeline with historical tracking.

## Running

```bash
cd examples/43-code-health
make run
```

## Health Metrics

algitex tracks these key metrics:

| Category | Metric | Target |
|----------|--------|--------|
| Complexity | Average CC | < 1.8 |
| Complexity | Max CC | < 20 |
| Complexity | Critical functions | 0 |
| Organization | God modules | 0 |
| Organization | High-CC functions | < 4 |
| Duplication | Duplicate clusters | 0 |
| Dependencies | Circular cycles | 0 |
| Documentation | Doc coverage | > 80% |
| Documentation | Type coverage | > 90% |

## Analysis Pipeline

```
code2llm  →  vallm  →  redup  →  algitex integration
   ↓            ↓         ↓            ↓
  AST      4-tier     Duplicate   Health score
  metrics  validation detection   & trends
```

## Commands

```bash
# Run analysis
algitex analyze

# Store metrics for historical tracking
algitex analyze --store-metrics

# View trends
algitex metrics history --chart

# Compare to baseline
algitex metrics compare --baseline 2026-03-01

# Check thresholds
algitex metrics check-thresholds --max-cc 15
```

## CI/CD Integration

```yaml
name: Code Health Check
on: [pull_request]

jobs:
  health:
    steps:
      - run: algitex analyze
      - run: algitex metrics check-thresholds \
               --max-cc 15 --max-avg-cc 2.5
```

## Regression Prevention

- Pre-commit hooks block CC-increasing commits
- PR checks fail on new critical functions
- Sprint goals: reduce X critical functions
- Health dashboards visible to team

## Files

- `main.py` - Demonstration of code health monitoring
- `Makefile` - Standard run/test/clean targets
