# `metrics`

Metrics collection and reporting for algitex.

Tracks:
- Token usage per tier (algorithmic, micro, big LLM)
- Success/failure rates
- Cache hit rates
- Execution time per task type
- Cost estimates

Usage:
    from algitex.metrics import MetricsCollector, MetricsReporter
    
    metrics = MetricsCollector()
    metrics.record_llm_call(tier="micro", tokens_in=500, tokens_out=200, success=True)
    
    reporter = MetricsReporter(metrics)
    reporter.print_dashboard()


## Functions

### `get_metrics`

```python
def get_metrics() -> MetricsCollector
```

Get or create global metrics collector.

### `reset_metrics`

```python
def reset_metrics() -> None
```

Reset global metrics.

## Classes

### `LLMCall`

Single LLM call record.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

### `FixResult`

Single fix execution record.

### `MetricsCollector`

Collect metrics during algitex operations.

**Methods:**

#### `__init__`

```python
def __init__(self, storage_path: Optional[str]=None)
```

#### `record_llm_call`

```python
def record_llm_call(self, tier: str, model: str, tokens_in: int, tokens_out: int, duration_ms: float, success: bool, cached: bool=False, task_category: str='') -> None
```

Record an LLM API call.

#### `record_fix`

```python
def record_fix(self, tier: str, category: str, file: str, line: int, success: bool, duration_ms: float, used_llm: bool=False) -> None
```

Record a fix execution.

#### `get_tier_stats`

```python
def get_tier_stats(self) -> Dict[str, Dict[str, Any]]
```

Get statistics by tier.

#### `estimate_cost`

```python
def estimate_cost(self) -> Dict[str, float]
```

Estimate total cost based on token usage.

#### `get_summary`

```python
def get_summary(self) -> Dict[str, Any]
```

Get complete metrics summary.

#### `save`

```python
def save(self) -> None
```

Persist metrics to disk.

#### `load`

```python
def load(self) -> None
```

Load previous metrics from disk.

#### `reset`

```python
def reset(self) -> None
```

Clear all metrics.

### `MetricsReporter`

Generate reports and dashboards from metrics.

**Methods:**

#### `__init__`

```python
def __init__(self, collector: MetricsCollector)
```

#### `print_dashboard`

```python
def print_dashboard(self, console=None) -> None
```

Print Rich dashboard to console.

#### `export_csv`

```python
def export_csv(self, path: str) -> None
```

Export metrics to CSV for analysis.
