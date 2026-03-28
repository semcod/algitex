# `todo.benchmark`

Benchmark utilities for TODO fixing performance measurement.

Usage:
    from algitex.todo.benchmark import benchmark_fix

    result = benchmark_fix("TODO.md", limit=100, workers=8)
    print(f"Throughput: {result.throughput_tps:.2f} tickets/sec")


## Functions

### `benchmark_sequential`

```python
def benchmark_sequential(tasks: list[TodoTask], dry_run: bool=True) -> BenchmarkResult
```

Run sequential benchmark.

### `benchmark_parallel`

```python
def benchmark_parallel(tasks: list[TodoTask], workers: int=8, dry_run: bool=True) -> BenchmarkResult
```

Run parallel benchmark.

### `benchmark_fix`

```python
def benchmark_fix(todo_path: str | Path='TODO.md', limit: int=10, workers: int=8, dry_run: bool=True, mode: str='parallel') -> BenchmarkResult
```

Run benchmark on TODO tasks.

    Args:
        todo_path: Path to TODO.md file
        limit: Number of tasks to benchmark
        workers: Number of parallel workers (for parallel mode)
        dry_run: If True, simulate fixes without applying
        mode: "parallel" or "sequential"

    Returns:
        BenchmarkResult with timing statistics
    

### `compare_modes`

```python
def compare_modes(todo_path: str | Path='TODO.md', limit: int=10, workers: int=8, dry_run: bool=True) -> dict
```

Compare parallel vs sequential execution.

    Returns:
        Dict with both results and speedup analysis
    

## Classes

### `BenchmarkResult`

Benchmark results for fix operations.

**Methods:**

#### `avg_time_ms`

```python
def avg_time_ms(self) -> float
```

#### `median_time_ms`

```python
def median_time_ms(self) -> float
```

#### `min_time_ms`

```python
def min_time_ms(self) -> float
```

#### `max_time_ms`

```python
def max_time_ms(self) -> float
```

#### `stdev_time_ms`

```python
def stdev_time_ms(self) -> float
```

#### `throughput_tps`

```python
def throughput_tps(self) -> float
```

Tickets per second.

#### `print_report`

```python
def print_report(self, detailed: bool=False) -> None
```

Print formatted benchmark report.
