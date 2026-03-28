# `tools.batch`

Batch processing — parallel LLM operations with rate limiting and retries.

Usage:
    from algitex.tools.batch import BatchProcessor
    
    # Define processing function
    def process_file(file_path):
        with open(file_path) as f:
            content = f.read()
        return ollama.generate(f"Analyze: {content}")
    
    # Create processor
    processor = BatchProcessor(
        worker_func=process_file,
        parallelism=4,
        rate_limit=2.0,  # requests per second
        max_retries=3
    )
    
    # Process files
    results = processor.process(file_list)


## Classes

### `BatchResult`

Result from batch processing.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary.

### `BatchStats`

Statistics for batch processing.

**Methods:**

#### `update`

```python
def update(self, results: List[BatchResult]) -> None
```

Update stats from results.

### `BatchProcessor`

Generic batch processor with rate limiting and retries.

**Methods:**

#### `__init__`

```python
def __init__(self, worker_func: Callable[[Any], Any], parallelism: int=4, rate_limit: float=2.0, max_retries: int=3, timeout: float=300.0, backoff_factor: float=2.0, progress: bool=True, save_results: bool=True, output_dir: str='.batch_results')
```

#### `process`

```python
def process(self, items: List[Any], progress_callback: Optional[Callable[[BatchResult], None]]=None) -> List[BatchResult]
```

Process items in parallel using 3-stage pipeline.

#### `get_successful`

```python
def get_successful(self) -> List[BatchResult]
```

Get only successful results.

#### `get_failed`

```python
def get_failed(self) -> List[BatchResult]
```

Get only failed results.

#### `filter_by_error`

```python
def filter_by_error(self, error_pattern: str) -> List[BatchResult]
```

Get results with specific error pattern.

### `FileBatchProcessor(BatchProcessor)`

Specialized batch processor for files.

**Methods:**

#### `__init__`

```python
def __init__(self, ollama_client, model: str=None, prompt_template: str=None, max_file_size: int=10000, **kwargs)
```

#### `find_files`

```python
def find_files(self, directory: Union[str, Path], pattern: str='*.py', exclude_patterns: List[str]=None) -> List[Path]
```

Find files matching pattern.

#### `process_directory`

```python
def process_directory(self, directory: Union[str, Path], pattern: str='*.py', **kwargs) -> List[BatchResult]
```

Process all files in directory.
