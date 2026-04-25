# Example 37: Performance Benchmarks

Demonstrates the benchmark framework for measuring performance.

## What it shows

- Quick benchmark (30 seconds)
- Cache performance testing
- Tier throughput comparison
- Memory profiling
- Full benchmark suite with export

## Running

```bash
cd examples/37-benchmarks
python main.py
```

# Quick benchmark
algitex benchmark quick

# Cache test
algitex benchmark cache --entries 100 --lookups 500

# Tier comparison
algitex benchmark tiers

# Memory profiling
algitex benchmark memory --lines 1000

# Full suite with export
algitex benchmark full --export results.json
```
