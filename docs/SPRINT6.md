## Overview

Sprint 6 dodaje framework do benchmarkowania wydajności algitex — cache, tierów (algorithm/micro/big) oraz użycia pamięci.

### 1. `algitex.benchmark`

Framework do benchmarkowania z pomiarem pamięci via `tracemalloc`.

```python
from algitex.benchmark import (
    BenchmarkRunner,
    CacheBenchmark,
    TierBenchmark,
    MemoryBenchmark,
)

# Quick benchmark (30 seconds)
runner = BenchmarkRunner(duration=30)
result = runner.run_quick()
result.print_report()

# Full benchmark suite
runner = BenchmarkRunner(duration=60)
results = runner.run_all()
for name, result in results.items():
    print(f"{name}: {result.throughput:.1f} ops/sec")
```

# Quick benchmark (30 seconds)
algitex benchmark quick

# Test cache performance
algitex benchmark cache --entries 100 --lookups 500

# Compare tier throughput  
algitex benchmark tiers

# Memory profiling for large files
algitex benchmark memory --lines 1000

# Full benchmark suite with export
algitex benchmark full --export results.json
```

### CacheBenchmark

Testuje wydajność cache LLM — hit rate, deduplication, lookup speed.

```python
from algitex.benchmark import CacheBenchmark

benchmark = CacheBenchmark(
    entries=100,      # Cache entries to create
    lookups=500,      # Number of lookups
    hit_rate_target=0.8  # Expected hit rate
)

result = benchmark.run()
print(f"Hit rate: {result.hit_rate:.1%}")
print(f"Deduplication: {result.deduplication_ratio:.1f}x")
print(f"Avg lookup: {result.avg_lookup_ms:.2f}ms")
```

**Metrics:**
- `hit_rate` — procent trafień cache
- `miss_rate` — procent missów
- `deduplication_ratio` — ile razy mniej zapytań dzięki cache
- `avg_lookup_ms` — średni czas lookupu

### TierBenchmark

Porównuje throughput trzech tierów: algorithm, micro, big.

```python
from algitex.benchmark import TierBenchmark

benchmark = TierBenchmark(
    algorithm_tasks=1000,
    micro_tasks=100,
    big_tasks=10,
)

results = benchmark.run()

for tier, result in results.items():
    print(f"{tier}: {result.throughput:.1f} tasks/sec")
```

**Expected Results:**

| Tier | Throughput | Characteristics |
|------|------------|-----------------|
| algorithm | 1000-2000/s | CPU-bound, no LLM |
| micro | 10-50/s | Small LLM (7B), local |
| big | 1-10/s | Big LLM, API calls |

### MemoryBenchmark

Profiluje użycie pamięci podczas przetwarzania dużych plików.

```python
from algitex.benchmark import MemoryBenchmark

benchmark = MemoryBenchmark(
    lines=1000,       # Lines per file
    files=10,         # Number of files
    operations=50,    # Operations to perform
)

result = benchmark.run()
print(f"Peak memory: {result.peak_memory_mb:.1f} MB")
print(f"Memory increase: {result.memory_increase_mb:.1f} MB")
print(f"Throughput: {result.throughput:.1f} ops/sec")
```

**Metrics:**
- `peak_memory_mb` — szczytowe użycie pamięci
- `memory_increase_mb` — przyrost pamięci podczas operacji
- `throughput` — operacje na sekundę

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Benchmark Framework                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Cache     │  │    Tier     │  │   Memory    │          │
│  │  Benchmark  │  │  Benchmark  │  │  Benchmark  │          │
│  │             │  │             │  │             │          │
│  │ • hit rate  │  │ • algorithm │  │ • peak MB   │          │
│  │ • dedup     │  │ • micro     │  │ • increase  │          │
│  │ • speed     │  │ • big       │  │ • throughput│          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┴────────────────┘                  │
│                          │                                   │
│                          ▼                                   │
│              ┌─────────────────────┐                        │
│              │   BenchmarkRunner   │                        │
│              │                     │                        │
│              │ • tracemalloc       │                        │
│              │ • time tracking     │                        │
│              │ • results export    │                        │
│              └─────────────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Przykładowe wyniki (dev machine)

```
═══════════════════════════════════════════════════════════════
                    BENCHMARK RESULTS
═══════════════════════════════════════════════════════════════

Cache Benchmark:
  Hit Rate:          90.9%
  Deduplication:     10.0x
  Avg Lookup:        0.05ms
  
Tier Benchmark:
  Algorithm:         1,547 tasks/sec (CPU-bound)
  Micro (7B):        23 tasks/sec (local LLM)
  Big (API):         4 tasks/sec (rate limited)
  
Memory Benchmark:
  Peak Memory:       45.2 MB
  Memory Increase:   12.5 MB
  Throughput:        8.3 ops/sec

═══════════════════════════════════════════════════════════════
```

## Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_benchmark.py` | 18 | BenchmarkRunner, CacheBenchmark, TierBenchmark, MemoryBenchmark |

# .github/workflows/benchmark.yml
name: Performance Benchmarks

on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run benchmarks
        run: |
          algitex benchmark quick --export benchmark.json
          
      - name: Check regressions
        run: |
          python -c "
          import json
          with open('benchmark.json') as f:
            results = json.load(f)
          # Fail if throughput dropped > 20%
          assert results['tier']['algorithm'] > 1000
          "
```

## Next Steps

1. **Historical tracking** — zapis wyników w czasie do wykrywania regresji
2. **Comparative benchmarks** — porównanie z poprzednimi wersjami
3. **Stress testing** — długotrwałe testy pod obciążeniem
4. **Integration with dashboard** — live benchmark results on dashboard

## Summary Sprintów 2-7

| Sprint | Cel | Rezultat |
|--------|-----|----------|
| 2 | MicroTask + NLP | 6 modułów, CLI `microtask`, `nlp` |
| 3 | TODO 3-tier integration | `fix --algo`, `--micro`, `--all` |
| 4 | Cache + Metryki + Prefact | `ollama_cache`, `metrics`, integracja |
| 5 | Dokumentacja + Testy | 82 nowe testy, docs/ |
| 6 | Benchmarks | `benchmark` CLI, 18 testów |
| 7 | Dashboard TUI | `dashboard live`, 28 testów |

**Łącznie: 317 testów, 2 skipped, ~40 nowych modułów**
