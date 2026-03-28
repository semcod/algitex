# `cli.metrics`

Metrics CLI commands for algitex.

## Functions

### `metrics_show`

```python
def metrics_show(storage: str=typer.Option('.algitex/metrics.json', '--storage', help='Metrics storage path'), export: Optional[str]=typer.Option(None, '--export', help='Export to CSV file'))
```

Show metrics dashboard.

### `metrics_clear`

```python
def metrics_clear(storage: str=typer.Option('.algitex/metrics.json', '--storage', help='Metrics storage path'), cache_dir: str=typer.Option('.algitex/cache', '--cache', help='LLM cache directory'))
```

Clear all metrics and cache.

### `metrics_cache`

```python
def metrics_cache(cache_dir: str=typer.Option('.algitex/cache', '--dir', help='Cache directory'), list_entries: bool=typer.Option(False, '--list', '-l', help='List all cache entries'), clear: bool=typer.Option(False, '--clear', '-c', help='Clear cache'))
```

Manage LLM response cache.

### `metrics_compare`

```python
def metrics_compare(storage: str=typer.Option('.algitex/metrics.json', '--storage', help='Metrics storage path'))
```

Compare tier performance (algorithm vs micro vs big LLM).
