# `benchmark`

Performance benchmarks for algitex.

Provides benchmarking infrastructure for measuring:
- Cache hit rates and latency
- Tier throughput (algorithmic, micro, big LLM)
- Memory usage for large files
- End-to-end pipeline performance

Usage:
    from algitex.benchmark import BenchmarkRunner, CacheBenchmark
    
    runner = BenchmarkRunner()
    runner.run_all()
    runner.print_report()


## Functions

### `run_quick_benchmark`

```python
def run_quick_benchmark() -> None
```

Run quick benchmark suite.

## Classes

### `BenchmarkResult`

Single benchmark run result.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

### `BenchmarkSuite`

Collection of benchmark results.

**Methods:**

#### `add`

```python
def add(self, result: BenchmarkResult) -> None
```

#### `summary`

```python
def summary(self) -> Dict[str, Any]
```

#### `print_table`

```python
def print_table(self) -> None
```

Print results as ASCII table.

### `BenchmarkRunner`

Main benchmark runner with memory tracking.

**Methods:**

#### `__init__`

```python
def __init__(self, warmup_iterations: int=3)
```

#### `run`

```python
def run(self, name: str, func: Callable, iterations: int=100, *args, **kwargs) -> BenchmarkResult
```

Run single benchmark.

#### `run_suite`

```python
def run_suite(self, name: str, benchmarks: Dict[str, tuple]) -> BenchmarkSuite
```

Run multiple benchmarks as a suite.

#### `print_report`

```python
def print_report(self) -> None
```

Print all benchmark results.

#### `export_json`

```python
def export_json(self, path: str) -> None
```

Export all results to JSON.

### `CacheBenchmark`

Benchmarks for LLM cache performance.

**Methods:**

#### `bench_cache_hit_rate`

```python
def bench_cache_hit_rate(cache_dir: str, entries: int=1000, lookups: int=5000) -> Dict[str, float]
```

Benchmark cache hit rate with synthetic data.

#### `bench_cache_deduplication`

```python
def bench_cache_deduplication(cache_dir: str, duplicates: int=100) -> Dict[str, Any]
```

Benchmark deduplication of identical prompts.

### `TierBenchmark`

Benchmarks for three-tier performance comparison.

**Methods:**

#### `bench_algorithmic_fix`

```python
def bench_algorithmic_fix() -> Dict[str, float]
```

Benchmark algorithmic (Tier 0) fix performance.

#### `bench_micro_llm_simulated`

```python
def bench_micro_llm_simulated() -> Dict[str, float]
```

Simulate micro LLM tier with delay.

#### `compare_tiers`

```python
def compare_tiers() -> Dict[str, Dict[str, float]]
```

Compare all three tiers.

### `MemoryBenchmark`

Memory profiling benchmarks.

**Methods:**

#### `profile_large_file_parsing`

```python
def profile_large_file_parsing(lines: int=10000) -> Dict[str, float]
```

Memory profile parsing large Python files.
