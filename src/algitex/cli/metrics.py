"""Metrics CLI commands for algitex."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import clickmd
from clickmd import command, option, argument
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()


@command()
@option("--storage", default=".algitex/metrics.json", help="Metrics storage path")
@option("--export", help="Export to CSV file")
def metrics_show(storage: str, export: Optional[str]):
    """Show metrics dashboard."""
    from algitex.metrics import MetricsCollector, MetricsReporter
    
    collector = MetricsCollector(storage)
    collector.load()
    
    reporter = MetricsReporter(collector)
    reporter.print_dashboard(console)
    
    if export:
        reporter.export_csv(export)
        console.print(f"\n[green]✓ Exported to {export}[/]")


@command()
@option("--storage", default=".algitex/metrics.json", help="Metrics storage path")
@option("--cache", default=".algitex/cache", help="LLM cache directory")
def metrics_clear(storage: str, cache: str):
    """Clear all metrics and cache."""
    from algitex.metrics import MetricsCollector
    from algitex.tools.ollama_cache import LLMCache
    
    console.print("[bold]Clearing metrics and cache...[/]")
    
    # Clear metrics
    collector = MetricsCollector(storage)
    collector.reset()
    collector.save()
    console.print(f"[green]✓ Cleared metrics: {storage}[/]")
    
    # Clear cache
    cache_obj = LLMCache(cache)
    count = cache_obj.clear()
    console.print(f"[green]✓ Cleared {count} cache entries from {cache}[/]")


@command()
@option("--dir", default=".algitex/cache", help="Cache directory")
@option("--list", "-l", "list_entries", is_flag=True, help="List all cache entries")
@option("--clear", "-c", "clear_cache", is_flag=True, help="Clear cache")
def metrics_cache(dir: str, list_entries: bool, clear_cache: bool):
    """Manage LLM response cache."""
    from algitex.tools.ollama_cache import LLMCache
    
    cache = LLMCache(dir)
    stats = cache.stats()
    
    if clear_cache:
        count = cache.clear()
        console.print(f"[green]✓ Cleared {count} cache entries[/]")
        return
    
    if list_entries:
        entries = cache.list_entries()
        if not entries:
            console.print("[yellow]Cache is empty[/]")
            return
        
        table = Table(title=f"Cache Entries ({len(entries)} total)")
        table.add_column("Hash", style="dim")
        table.add_column("Model")
        table.add_column("Age (h)", justify="right")
        table.add_column("Tokens", justify="right")
        
        for e in entries[:50]:  # Show first 50
            table.add_row(e["hash"][:16], e["model"], str(e["age_hours"]), str(e["tokens"]))
        
        console.print(table)
        if len(entries) > 50:
            console.print(f"[dim]... and {len(entries) - 50} more entries[/]")
        return
    
    # Show stats
    console.print(Panel(
        f"Entries: {stats['entries']}\n"
        f"Size: {stats['size_bytes'] / 1024:.1f} KB\n"
        f"Hits: {stats['hits']}\n"
        f"Misses: {stats['misses']}\n"
        f"Hit Rate: {stats['hit_rate']:.1%}",
        title="LLM Cache Stats",
        border_style="green"
    ))


@command()
@option("--storage", default=".algitex/metrics.json", help="Metrics storage path")
def metrics_compare(storage: str):
    """Compare tier performance (algorithm vs micro vs big LLM)."""
    from algitex.metrics import MetricsCollector
    
    collector = MetricsCollector(storage)
    collector.load()
    
    tier_stats = collector.get_tier_stats()
    costs = collector.estimate_cost()
    
    table = Table(title="Tier Comparison")
    table.add_column("Metric", style="bold")
    table.add_column("Algorithm (Tier 0)", justify="right")
    table.add_column("Micro LLM (Tier 1)", justify="right")
    table.add_column("Big LLM (Tier 2)", justify="right")
    
    # Calls
    table.add_row(
        "LLM Calls",
        str(tier_stats.get("algorithm", {}).get("calls", 0)),
        str(tier_stats.get("micro", {}).get("calls", 0)),
        str(tier_stats.get("big", {}).get("calls", 0)),
    )
    
    # Tokens
    algo_tokens = tier_stats.get("algorithm", {}).get("tokens_in", 0) + tier_stats.get("algorithm", {}).get("tokens_out", 0)
    micro_tokens = tier_stats.get("micro", {}).get("tokens_in", 0) + tier_stats.get("micro", {}).get("tokens_out", 0)
    big_tokens = tier_stats.get("big", {}).get("tokens_in", 0) + tier_stats.get("big", {}).get("tokens_out", 0)
    
    table.add_row(
        "Tokens",
        f"{algo_tokens:,}" if algo_tokens else "-",
        f"{micro_tokens:,}" if micro_tokens else "-",
        f"{big_tokens:,}" if big_tokens else "-",
    )
    
    # Success rate
    for tier in ["algorithm", "micro", "big"]:
        stats = tier_stats.get(tier, {})
        total = stats.get("success", 0) + stats.get("failure", 0)
        if total > 0:
            rate = stats.get("success", 0) / total
            tier_stats[tier]["success_rate"] = f"{rate:.1%}"
        else:
            tier_stats[tier]["success_rate"] = "-"
    
    table.add_row(
        "Success Rate",
        tier_stats.get("algorithm", {}).get("success_rate", "-"),
        tier_stats.get("micro", {}).get("success_rate", "-"),
        tier_stats.get("big", {}).get("success_rate", "-"),
    )
    
    # Cost
    table.add_row(
        "Est. Cost",
        "Free",
        f"${costs.get('micro', 0):.4f}" if costs.get('micro') else "-",
        f"${costs.get('big', 0):.4f}" if costs.get('big') else "-",
    )
    
    console.print(table)
    
    total_cost = sum(v for k, v in costs.items() if k != "total")
    console.print(f"\n[dim]Total estimated cost: ${total_cost:.4f}[/]")
