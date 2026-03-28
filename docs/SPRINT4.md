# Sprint 4: Cache LLM + Metryki + Prefact Integration

## Overview

Sprint 4 dodaje trzy główne komponenty do algitex:

1. **LLM Cache** — deduplikacja identycznych promptów dla Ollama
2. **Metryki** — tracking tokenów, kosztów, success rate per tier
3. **Prefact Integration** — współdzielenie reguł między algitex a prefact

## Nowe moduły

### 1. `algitex.tools.ollama_cache`

Cache warstwa dla `OllamaClient` — automatyczna deduplikacja identycznych promptów.

```python
from algitex.tools.ollama_cache import CachedOllamaClient, LLMCache

# Client z automatycznym cachingiem
client = CachedOllamaClient(
    host="http://localhost:11434",
    cache_dir=".algitex/cache",
    cache_ttl_hours=24.0,
)

# Ten sam prompt = cache hit, bez LLM call
response1 = client.generate("Fix this code: ...", model="qwen2.5-coder:7b")
response2 = client.generate("Fix this code: ...", model="qwen2.5-coder:7b")  # Cached!

# Stats
metrics = client.get_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
```

#### `LLMCache` — disk-based cache

```python
cache = LLMCache(cache_dir=".algitex/cache", ttl_hours=24.0)

# Store
cache.set(prompt="Hello", model="qwen2.5-coder:7b", response="Hi!", tokens_prompt=10, tokens_response=5)

# Retrieve
entry = cache.get(prompt="Hello", model="qwen2.5-coder:7b")
if entry:
    print(f"Cached response: {entry.response}")

# Stats
stats = cache.stats()  # hits, misses, hit_rate, entries, size_bytes
```

### 2. `algitex.metrics`

Tracking LLM calls i fix results z estymacją kosztów.

```python
from algitex.metrics import MetricsCollector, MetricsReporter, get_metrics

# Per-session tracking
collector = MetricsCollector()

# Record LLM call
collector.record_llm_call(
    tier="micro",           # "algorithm", "micro", "big"
    model="qwen2.5-coder:7b",
    tokens_in=500,
    tokens_out=200,
    duration_ms=1500.0,
    success=True,
    cached=False,
    task_category="magic",
)

# Record fix result
collector.record_fix(
    tier="algorithm",
    category="unused_import",
    file="src/foo.py",
    line=10,
    success=True,
    duration_ms=50.0,
    used_llm=False,
)

# Get stats per tier
stats = collector.get_tier_stats()
print(f"Micro calls: {stats['micro']['calls']}")

# Cost estimation (USD)
costs = collector.estimate_cost()
print(f"Total cost: ${costs['total']:.4f}")

# Summary with all metrics
summary = collector.get_summary()
```

#### Cost rates (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| Local (Ollama) | $0 | $0 |
| Claude 3.5 Sonnet | $3 | $15 |
| Claude 3 Haiku | $0.25 | $1.25 |
| GPT-4o | $2.50 | $10 |
| GPT-4o-mini | $0.15 | $0.60 |

### 3. `algitex.prefact_integration`

Adapter do integracji z `prefact` — umożliwia użycie reguł prefact w algitex.

```python
from algitex.prefact_integration import PrefactRuleAdapter, SharedRuleEngine

# Check if prefact is available
adapter = PrefactRuleAdapter()
if adapter.is_available():
    # Scan file with prefact
    issues = adapter.scan_file("src/myfile.py")
    
    # Specific rule checks
    sorted_issues = adapter.check_sorted_imports("src/myfile.py")
    relative_issues = adapter.check_relative_imports("src/myfile.py")
    
    # Scan directory
    all_issues = adapter.scan_directory("./src")
```

#### Unified engine

```python
from algitex.prefact_integration import SharedRuleEngine

engine = SharedRuleEngine()

# Analyze with both prefact and native algitex rules
results = engine.analyze("src/myfile.py")
# Returns: {"prefact": [...], "algitex": [...]}

# Get all issues combined
all_issues = engine.get_all_issues("src/myfile.py")
```

### 4. `algitex.shared_rules`

Współdzielone reguły między algitex a prefact.

```python
from algitex.shared_rules import get_registry, SortedImportsRule, RelativeImportRule

# Global registry with built-in rules
registry = get_registry()

# List all rules
for rule in registry.list_rules():
    print(f"{rule.rule_id}: {rule.tier}")

# Check file
results = registry.check_file("src/myfile.py")
# Returns: {"sorted_imports": [violations], "relative_imports": [violations]}
```

#### Creating custom shared rules

```python
from algitex.shared_rules import SharedRule, RuleContext, RuleViolation

class MyCustomRule(SharedRule):
    rule_id = "my_rule"
    description = "Check for something"
    tier = "algorithm"  # "algorithm", "micro", "big"
    fixable = True
    severity = "warning"
    
    def check(self, context: RuleContext) -> List[RuleViolation]:
        violations = []
        # Analyze context.source_code
        # ...
        return violations
    
    def _apply_fix(self, context: RuleContext, violation: RuleViolation) -> Optional[str]:
        # Return fixed source code
        return modified_source

# Register
from algitex.shared_rules import get_registry
get_registry().register(MyCustomRule())
```

## CLI Commands

### `algitex metrics`

```bash
# Show dashboard
algitex metrics show

# Show with export to CSV
algitex metrics show --export metrics.csv

# Compare tier performance
algitex metrics compare

# Cache management
algitex metrics cache              # Show cache stats
algitex metrics cache --list       # List all entries
algitex metrics cache --clear      # Clear cache

# Clear everything
algitex metrics clear
```

## Test Coverage

Sprint 4 dodaje 82 nowe testy:

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_ollama_cache.py` | 17 | Cache operations, TTL, stats |
| `test_metrics.py` | 24 | Collector, Reporter, cost estimation |
| `test_shared_rules.py` | 28 | Rules, Registry, violations |
| `test_prefact_integration.py` | 20 | Adapter, Engine, helpers |
| `test_cli_metrics.py` | 13 | CLI integration |

**Total: 102 tests, 2 skipped** (wymagają Ollama server)

## Integration z istniejącym kodem

### MicroTask executor z cache

```python
from algitex.microtask.executor import MicroTaskExecutor
from algitex.tools.ollama_cache import CachedOllamaClient

# Executor automatycznie używa CachedOllamaClient jeśli dostępny
executor = MicroTaskExecutor(
    ollama_client=CachedOllamaClient(cache_dir=".algitex/cache")
)
```

### Todo fix z metrykami

```python
from algitex.todo import parallel_fix_and_update
from algitex.metrics import get_metrics

# Fix z automagicznym trackingiem
result = parallel_fix_and_update("TODO.md", workers=8)

# Metrics są zbierane automatycznie
metrics = get_metrics()
metrics.save()
```

## Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                    Algitex Sprint 4                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │  LLM Cache  │  │  Metrics    │  │  Prefact Adapter    │   │
│  │  (disk)     │  │  (JSON)     │  │  (subprocess)       │   │
│  ├─────────────┤  ├─────────────┤  ├─────────────────────┤   │
│  │ • TTL       │  │ • Tokens    │  │ • sorted_imports    │   │
│  │ • dedup     │  │ • Cost      │  │ • relative_imports  │   │
│  │ • stats     │  │ • Tiers     │  │ • scan_file/dir     │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
│         │                │                  │               │
│         └────────────────┴──────────────────┘               │
│                          │                                  │
│              ┌───────────┴───────────┐                      │
│              │    Shared Rules       │                      │
│              │  (algitex↔prefact)    │                      │
│              └───────────────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Sprint 5**: Dokumentacja API + benchmark performance
2. **Future**: Redis backend dla cache, webhook metryki, real-time dashboard
