"""Dashboard CLI commands for algitex."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def dashboard_live(
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Duration in seconds (default: run until Ctrl+C)"),
    refresh: float = typer.Option(1.0, "--refresh", "-r", help="Refresh rate in seconds"),
    demo: bool = typer.Option(False, "--demo", help="Run in demo mode with simulated data"),
):
    """Launch live TUI dashboard for real-time monitoring.
    
    Shows:
    - Cache performance (hit rate, entries, size)
    - Tier progress (algorithm, micro, big LLM)
    - Operation status and throughput
    - System resource usage
    
    Examples:
        algitex dashboard live                    # Run until Ctrl+C
        algitex dashboard live --duration 60      # Run for 60 seconds
        algitex dashboard live --demo             # Demo with simulated data
    """
    from algitex.dashboard import LiveDashboard, show_quick_dashboard
    
    if demo:
        show_quick_dashboard(duration=duration or 30.0)
        return
    
    try:
        dashboard = LiveDashboard(refresh_rate=refresh)
        dashboard.start()
        
        console.print(Panel(
            "[bold green]Live Dashboard Started[/]\n\n"
            f"Refresh rate: {refresh}s\n"
            f"Press Ctrl+C to stop",
            title="Algitex Dashboard",
            border_style="green",
        ))
        
        if duration:
            import time
            time.sleep(duration)
        else:
            # Run until interrupted
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped[/]")
    finally:
        dashboard.stop()


def dashboard_monitor(
    cache_dir: str = typer.Option(".algitex/cache", "--cache", help="Cache directory to monitor"),
    metrics_file: str = typer.Option(".algitex/metrics.json", "--metrics", help="Metrics file to monitor"),
):
    """Monitor existing cache and metrics files.
    
    Reads from existing cache/metrics and displays current state.
    """
    from algitex.tools.ollama_cache import LLMCache
    from algitex.metrics import MetricsCollector
    from rich.table import Table
    
    # Cache stats
    cache = LLMCache(cache_dir)
    cache_stats = cache.stats()
    
    # Metrics
    metrics = MetricsCollector(metrics_file)
    metrics.load()
    summary = metrics.get_summary()
    
    # Display
    console.print("\n[bold]Cache Status[/]")
    cache_table = Table()
    cache_table.add_column("Metric", style="bold")
    cache_table.add_column("Value", justify="right")
    cache_table.add_row("Entries", str(cache_stats["entries"]))
    cache_table.add_row("Size", f"{cache_stats['size_bytes'] / 1024 / 1024:.2f} MB")
    cache_table.add_row("Hit Rate", f"{cache_stats['hit_rate']:.1%}")
    cache_table.add_row("Hits", str(cache_stats["hits"]))
    cache_table.add_row("Misses", str(cache_stats["misses"]))
    console.print(cache_table)
    
    console.print("\n[bold]Metrics Summary[/]")
    metrics_table = Table()
    metrics_table.add_column("Metric", style="bold")
    metrics_table.add_column("Value", justify="right")
    metrics_table.add_row("LLM Calls", str(summary["llm_calls"]))
    metrics_table.add_row("Cached Calls", f"{summary['cache_hit_rate']:.1%}")
    metrics_table.add_row("Est. Cost", f"${summary['estimated_cost_usd']:.4f}")
    metrics_table.add_row("Fix Attempts", str(summary["fix_attempts"]))
    metrics_table.add_row("Success Rate", f"{summary['fix_success_rate']:.1%}")
    console.print(metrics_table)
    
    console.print("\n[dim]Use 'dashboard live' for real-time monitoring[/]")


def dashboard_export(
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, prometheus"),
    output: str = typer.Option("dashboard.json", "--output", "-o", help="Output file"),
    duration: int = typer.Option(60, "--duration", "-d", help="Collection duration in seconds"),
):
    """Export dashboard data to file (JSON or Prometheus format).
    
    Collects metrics for specified duration and exports to file.
    """
    import json
    import time
    from algitex.tools.ollama_cache import LLMCache
    from algitex.metrics import MetricsCollector
    
    console.print(f"[bold]Collecting metrics for {duration} seconds...[/]")
    
    # Collect data points
    data_points = []
    start = time.time()
    
    while time.time() - start < duration:
        cache = LLMCache(".algitex/cache")
        metrics = MetricsCollector(".algitex/metrics.json")
        metrics.load()
        
        data_points.append({
            "timestamp": time.time(),
            "cache": cache.stats(),
            "metrics": metrics.get_summary(),
        })
        
        time.sleep(1)
    
    # Export
    if format == "json":
        Path(output).write_text(json.dumps(data_points, indent=2))
        console.print(f"[green]✓ Exported {len(data_points)} data points to {output}[/]")
    
    elif format == "prometheus":
        # Simple Prometheus-style output
        lines = []
        for dp in data_points:
            ts = dp["timestamp"]
            cache = dp["cache"]
            lines.append(f'cache_entries{{}} {cache["entries"]} {int(ts * 1000)}')
            lines.append(f'cache_hits{{}} {cache["hits"]} {int(ts * 1000)}')
            lines.append(f'cache_hit_rate{{}} {cache["hit_rate"]} {int(ts * 1000)}')
        
        Path(output).write_text("\n".join(lines))
        console.print(f"[green]✓ Exported Prometheus metrics to {output}[/]")
    
    else:
        console.print(f"[red]Unknown format: {format}[/]")


# Import at the end to avoid circular dependency
from pathlib import Path
