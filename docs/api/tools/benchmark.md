# `tools.benchmark`

Model benchmarking — compare LLM models on standardized tasks.

Usage:
    from algitex.tools.benchmark import ModelBenchmark
    
    # Create benchmark
    benchmark = ModelBenchmark(ollama_client)
    
    # Add tasks
    benchmark.add_task("code_completion", prompt, expected_keywords)
    
    # Run comparison
    results = benchmark.compare_models(["model1", "model2"])
    
    # Print results
    benchmark.print_results(results)


## Classes

### `Task`

Benchmark task definition.

**Methods:**

#### `evaluate_quality`

```python
def evaluate_quality(self, response: str) -> float
```

Evaluate response quality (0-5 scale).

### `TaskResult`

Result for a single model on a single task.

**Methods:**

#### `tokens_per_second`

```python
def tokens_per_second(self) -> float
```

Calculate tokens per second.

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary.

### `BenchmarkResults`

Complete benchmark results.

**Methods:**

#### `get_model_results`

```python
def get_model_results(self, model: str) -> List[TaskResult]
```

Get all results for a model.

#### `get_task_results`

```python
def get_task_results(self, task_id: str) -> List[TaskResult]
```

Get all results for a task.

#### `get_best_model`

```python
def get_best_model(self, task_id: str, metric: str='quality') -> Optional[str]
```

Get best model for a task by metric.

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary.

#### `get_summary`

```python
def get_summary(self) -> Dict[str, Any]
```

Get summary statistics.

### `ModelBenchmark`

Benchmark models on standardized tasks.

**Methods:**

#### `__init__`

```python
def __init__(self, ollama_client, default_tasks: bool=True)
```

#### `add_task`

```python
def add_task(self, task: Task)
```

Add a custom task.

#### `add_custom_task`

```python
def add_custom_task(self, task_id: str, name: str, prompt: str, expected_keywords: List[str], **kwargs)
```

Add a custom task by parameters.

#### `run_single_task`

```python
def run_single_task(self, model: str, task: Task) -> TaskResult
```

Run a single benchmark task.

#### `compare_models`

```python
def compare_models(self, models: List[str], tasks: Optional[List[str]]=None, progress: bool=True) -> BenchmarkResults
```

Compare models on all tasks.

#### `print_results`

```python
def print_results(self, results: BenchmarkResults, format: str='table')
```

Print benchmark results.

#### `save_results`

```python
def save_results(self, results: BenchmarkResults, filename: Optional[str]=None)
```

Save results to JSON file.

#### `load_results`

```python
def load_results(self, filename: str) -> BenchmarkResults
```

Load results from JSON file.
