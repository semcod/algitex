# `tools.telemetry`

LLM cost & performance telemetry for algitex pipelines.

## Classes

### `TraceSpan`

Single operation span.

**Methods:**

#### `duration_s`

```python
def duration_s(self) -> float
```

#### `finish`

```python
def finish(self, status='ok', **kwargs) -> None
```

### `Telemetry`

Track costs, tokens, time across an algitex pipeline run.

**Methods:**

#### `__init__`

```python
def __init__(self, project_name: str, run_id: Optional[str]=None)
```

#### `span`

```python
def span(self, name: str, tool: str='algitex') -> TraceSpan
```

Create a new span for tracking.

#### `total_cost`

```python
def total_cost(self) -> float
```

#### `total_tokens`

```python
def total_tokens(self) -> int
```

#### `total_duration`

```python
def total_duration(self) -> float
```

#### `error_count`

```python
def error_count(self) -> int
```

#### `summary`

```python
def summary(self) -> Dict[str, Any]
```

Get a summary of the telemetry data.

#### `push_to_langfuse`

```python
def push_to_langfuse(self) -> None
```

Push traces to Langfuse for visualization.

#### `save`

```python
def save(self, output_dir: str='.algitex') -> None
```

Save telemetry data to local file.

#### `report`

```python
def report(self) -> str
```

Generate a human-readable report.
