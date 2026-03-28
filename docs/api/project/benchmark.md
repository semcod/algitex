# `project.benchmark`

Benchmarking mixins for Project class.

## Classes

### `BenchmarkMixin`

Model benchmarking functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self, ollama_client) -> None
```

#### `benchmark_models`

```python
def benchmark_models(self, models: List[str], tasks: Optional[List[str]]=None) -> dict
```

Benchmark models on tasks.

#### `add_benchmark_task`

```python
def add_benchmark_task(self, task_id: str, name: str, prompt: str, expected_keywords: List[str])
```

Add a custom benchmark task.

#### `print_benchmark_results`

```python
def print_benchmark_results(self, results: dict, format: str='table') -> None
```

Print benchmark results from dict.
