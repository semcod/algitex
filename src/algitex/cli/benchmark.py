"""Benchmark CLI commands for algitex."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def benchmark_cache(
    entries: int = typer.Option(100, "--entries", "-e", help="Number of cache entries"),
    lookups: int = typer.Option(500, "--lookups", "-l", help="Number of lookups"),
):
    """Benchmark LLM cache performance."""
    from algitex.benchmark import CacheBenchmark
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running cache benchmark...", total=None)
            
            result = CacheBenchmark.bench_cache_hit_rate(
                cache_dir=tmpdir,
                entries=entries,
                lookups=lookups,
            )
        
        # Display results
        console.print(Panel(
            f"[bold]Cache Hit Rate Benchmark[/]\n\n"
            f"Entries: {result['entries']:,}\n"
            f"Lookups: {result['lookups']:,}\n"
            f"Hits: {result['hits']:,}\n"
            f"Misses: {result['misses']:,}\n"
            f"Hit Rate: [green]{result['hit_rate']:.1%}[/]\n"
            f"Throughput: {result['throughput']:,.0f} ops/sec\n"
            f"Latency: {result['latency_ms']:.3f} ms/op",
            border_style="green",
        ))


def benchmark_tiers():
    """Benchmark all three tiers (algorithm, micro, big)."""
    from algitex.benchmark import TierBenchmark
    
    console.print("[bold]Running tier benchmarks...[/]\n")
    
    results = TierBenchmark.compare_tiers()
    
    table = Table(title="Tier Performance Comparison")
    table.add_column("Tier", style="bold")
    table.add_column("Throughput", justify="right")
    table.add_column("Latency", justify="right")
    table.add_column("Notes")
    
    for tier_name, result in results.items():
        tier_label = result.get('tier', tier_name)
        throughput = result.get('throughput') or result.get('estimated_throughput', 0)
        latency_ms = result.get('duration_ms', 0) / result.get('iterations', 1)
        note = result.get('note', '')
        
        # Format throughput
        if throughput >= 1000:
            throughput_str = f"{throughput/1000:.1f}K ops/sec"
        else:
            throughput_str = f"{throughput:.1f} ops/sec"
        
        # Format latency
        if latency_ms < 1:
            latency_str = f"{latency_ms*1000:.2f} µs"
        elif latency_ms < 1000:
            latency_str = f"{latency_ms:.2f} ms"
        else:
            latency_str = f"{latency_ms/1000:.2f} s"
        
        table.add_row(tier_label, throughput_str, latency_str, note)
    
    console.print(table)
    
    console.print("\n[dim]Note: 'big' tier requires actual LLM API keys for real benchmarking[/]")


def benchmark_memory(
    lines: int = typer.Option(1000, "--lines", "-n", help="Lines in test file"),
):
    """Benchmark memory usage for large file processing."""
    from algitex.benchmark import MemoryBenchmark
    
    console.print(f"[bold]Profiling memory with {lines:,} lines...[/]\n")
    
    result = MemoryBenchmark.profile_large_file_parsing(lines=lines)
    
    console.print(Panel(
        f"[bold]Memory Profile Results[/]\n\n"
        f"Source lines: {result['lines']:,}\n"
        f"Source size: {result['source_size_mb']:.2f} MB\n"
        f"Memory used: {result['memory_used_mb']:.2f} MB\n"
        f"Efficiency: {result['memory_per_1k_lines_kb']:.2f} KB per 1K lines",
        border_style="blue",
    ))


def benchmark_full(
    export: Optional[str] = typer.Option(None, "--export", "-o", help="Export to JSON file"),
    quick: bool = typer.Option(False, "--quick", help="Quick mode (smaller datasets)"),
):
    """Run full benchmark suite."""
    from algitex.benchmark import BenchmarkRunner, CacheBenchmark, TierBenchmark, MemoryBenchmark
    from algitex.benchmark import run_quick_benchmark
    
    if quick:
        run_quick_benchmark()
        return
    
    runner = BenchmarkRunner(warmup_iterations=2)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "cache"
        
        # Define benchmarks
        benchmarks = {
            "cache_hit_rate": (
                lambda: CacheBenchmark.bench_cache_hit_rate(str(cache_dir), 100, 500),
                1, [], {}
            ),
            "cache_dedup": (
                lambda: CacheBenchmark.bench_cache_deduplication(str(cache_dir), 50),
                1, [], {}
            ),
            "tier_algorithm": (
                TierBenchmark.bench_algorithmic_fix, 1, [], {}
            ),
        }
        
        console.print("[bold]Running full benchmark suite...[/]\n")
        
        suite = runner.run_suite("algitex_performance", benchmarks)
        
        # Print results
        suite.print_table()
        
        if export:
            runner.export_json(export)
            console.print(f"\n[green]✓ Exported to {export}[/]")


def benchmark_quick():
    """Quick benchmark (30 seconds)."""
    from algitex.benchmark import run_quick_benchmark
    
    console.print("[bold]Running quick benchmark...[/]\n")
    run_quick_benchmark()
