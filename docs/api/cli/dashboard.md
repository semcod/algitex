# `cli.dashboard`

Dashboard CLI commands for algitex.

## Functions

### `dashboard_live`

```python
def dashboard_live(duration: Optional[int]=typer.Option(None, '--duration', '-d', help='Duration in seconds (default: run until Ctrl+C)'), refresh: float=typer.Option(1.0, '--refresh', '-r', help='Refresh rate in seconds'), demo: bool=typer.Option(False, '--demo', help='Run in demo mode with simulated data'))
```

Launch live TUI dashboard for real-time monitoring.
    
    Shows:
    - Cache performance (hit rate, entries, size)
    - Tier progress (algorithm, micro, big LLM)
    - Operation status and throughput
    - System resource usage
    
    Examples:
        algitex dashboard live                    # Run until Ctrl+C
        algitex dashboard live --duration 60      # Run for 60 seconds
        algitex dashboard live --demo             # Demo with simulated data
    

### `dashboard_monitor`

```python
def dashboard_monitor(cache_dir: str=typer.Option('.algitex/cache', '--cache', help='Cache directory to monitor'), metrics_file: str=typer.Option('.algitex/metrics.json', '--metrics', help='Metrics file to monitor'))
```

Monitor existing cache and metrics files.
    
    Reads from existing cache/metrics and displays current state.
    

### `dashboard_export`

```python
def dashboard_export(format: str=typer.Option('json', '--format', '-f', help='Export format: json, prometheus'), output: str=typer.Option('dashboard.json', '--output', '-o', help='Output file'), duration: int=typer.Option(60, '--duration', '-d', help='Collection duration in seconds'))
```

Export dashboard data to file (JSON or Prometheus format).
    
    Collects metrics for specified duration and exports to file.
    
