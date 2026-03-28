# `project.batch`

Batch processing mixins for Project class.

## Classes

### `BatchMixin`

Batch processing functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self, path: str, ollama_client) -> None
```

#### `batch_analyze`

```python
def batch_analyze(self, directory: str='.', pattern: str='*.py', parallelism: Optional[int]=None, rate_limit: Optional[float]=None) -> dict
```

Batch analyze files in directory.

#### `create_batch_processor`

```python
def create_batch_processor(self, worker_func: Callable, parallelism: int=4, rate_limit: float=2.0, **kwargs) -> BatchProcessor
```

Create a custom batch processor.
