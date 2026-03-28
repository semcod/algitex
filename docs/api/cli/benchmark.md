# `cli.benchmark`

Benchmark CLI commands for algitex.

## Functions

### `benchmark_cache`

```python
def benchmark_cache(entries: int=typer.Option(100, '--entries', '-e', help='Number of cache entries'), lookups: int=typer.Option(500, '--lookups', '-l', help='Number of lookups'))
```

Benchmark LLM cache performance.

### `benchmark_tiers`

```python
def benchmark_tiers()
```

Benchmark all three tiers (algorithm, micro, big).

### `benchmark_memory`

```python
def benchmark_memory(lines: int=typer.Option(1000, '--lines', '-n', help='Lines in test file'))
```

Benchmark memory usage for large file processing.

### `benchmark_full`

```python
def benchmark_full(export: Optional[str]=typer.Option(None, '--export', '-o', help='Export to JSON file'), quick: bool=typer.Option(False, '--quick', help='Quick mode (smaller datasets)'))
```

Run full benchmark suite.

### `benchmark_quick`

```python
def benchmark_quick()
```

Quick benchmark (30 seconds).
