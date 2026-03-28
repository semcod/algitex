# Sprint 7: Real-time Dashboard TUI

## Overview

Sprint 7 dodaje interaktywny dashboard TUI (Text User Interface) dla monitorowania operacji algitex w czasie rzeczywistym.

## Nowe moduły

### 1. `algitex.dashboard`

Live dashboard z komponentami Rich.

```python
from algitex.dashboard import LiveDashboard, SimpleProgressTracker

# Full dashboard
dashboard = LiveDashboard(refresh_rate=1.0)
dashboard.start()

# Update metrics
dashboard.update_cache_stats(hits=100, misses=10, entries=50)
dashboard.update_tier_progress("micro", current=25, total=100, throughput=10.0)

dashboard.stop()

# Simple progress tracking
with SimpleProgressTracker() as tracker:
    tracker.add_task("Processing", total=100)
    for i in range(100):
        tracker.update("Processing", advance=1)
```

#### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Algitex Live Dashboard — Status: micro | big                    │
├──────────────────────────┬──────────────────────────────────────┤
│ [Cache]                  │ [Tiers]                              │
│ Entries: 50              │ Tier    Progress   Status Throughput │
│ Size: 1.50 MB            │ algorithm 100/100 done     23.7K/s  │
│ Hits: 100                │ micro      25/100 running    20.0/s  │
│ Misses: 10               │ big         0/50  idle        0.5/s  │
│ Hit Rate: 90.9%          │                                      │
├──────────────────────────┴──────────────────────────────────────┤
│ Processed: 125 | Success: 120 | Failed: 5 | Press Ctrl+C        │
└─────────────────────────────────────────────────────────────────┘
```

### 2. CLI Commands

```bash
# Live dashboard (runs until Ctrl+C)
algitex dashboard live

# Demo mode with simulated data
algitex dashboard live --demo --duration 30

# Monitor existing cache/metrics
algitex dashboard monitor --cache .algitex/cache --metrics .algitex/metrics.json

# Export to JSON for analysis
algitex dashboard export --format json --output metrics.json --duration 60

# Export Prometheus format
algitex dashboard export --format prometheus --output metrics.prom
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Algitex Dashboard                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │  LiveDashboard  │    │SimpleProgress   │                  │
│  │                 │    │Tracker          │                  │
│  │ • Cache panel   │    │                 │                  │
│  │ • Tiers panel   │    │ • Progress bars │                  │
│  │ • Header/footer │    │ • ETA tracking  │                  │
│  └────────┬────────┘    └─────────────────┘                  │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────┐                   │
│  │           Rich Live Display            │                   │
│  │  ┌───────┐ ┌───────┐ ┌───────────┐   │                   │
│  │  │Layout │ │Panel  │ │Progress   │   │                   │
│  │  │Table  │ │Text   │ │BarColumn  │   │                   │
│  │  └───────┘ └───────┘ └───────────┘   │                   │
│  └─────────────────────────────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Komponenty

### TierState

```python
@dataclass
class TierState:
    name: str
    current: int = 0
    total: int = 0
    success: int = 0
    failed: int = 0
    throughput: float = 0.0
    active: bool = False
    
    @property
    def percent(self) -> float
    @property
    def eta_seconds(self) -> float
```

### CacheState

```python
@dataclass
class CacheState:
    hits: int = 0
    misses: int = 0
    entries: int = 0
    size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float
    @property
    def size_mb(self) -> float
```

## Integracja z operacjami

### Podczas `todo fix --all`

```python
from algitex.dashboard import LiveDashboard
from algitex.todo import parallel_fix_and_update, MicroFixer

dashboard = LiveDashboard()
dashboard.start()

try:
    # Phase 1: Algorithm
    dashboard.update_tier_progress("algorithm", active=True, total=len(algo_tasks))
    result = parallel_fix_and_update(...)
    dashboard.update_tier_progress("algorithm", current=result['fixed'], success=result['fixed'])
    
    # Phase 2: Micro
    dashboard.update_tier_progress("micro", active=True, total=len(micro_tasks))
    fixer = MicroFixer(...)
    # ... update progress during execution
    
    # Phase 3: Big
    dashboard.update_tier_progress("big", active=True, total=len(big_tasks))
    # ...
    
finally:
    dashboard.stop()
```

## Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_dashboard.py` | 28 | Dashboard, TierState, CacheState, ProgressTracker |

## Wyłączone z Sprint 7

WebSocket support został oznaczony jako `pending` — wymaga dodatkowych zależności (websockets, asyncio server) i będzie zaimplementowany w przyszłym sprincie jeśli potrzebny.

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

## Next Steps

1. **Release preparation** — wersjonowanie, changelog, git tag
2. **Sprint 8** — WebSocket + remote monitoring
3. **Integracja** — podłączenie dashboard do `todo fix` pipeline
4. **Documentation** — sphinx docs, README update

Co dalej?
