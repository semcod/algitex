"""Algorithmization subcommands for algitex CLI."""

from __future__ import annotations

import clickmd
from clickmd import command, option, argument
from rich.console import Console
from rich.table import Table

console = Console()


@command()
@option("--path", "-p", default=".")
def algo_discover(path: str) -> None:
    """Stage 1: Start trace collection from proxym."""
    from algitex.algo import Loop
    loop = Loop(path)
    loop.discover()
    console.print("\u2705 Discovery mode active. Traces will be collected from proxym.")
    console.print("Use your IDE normally \u2014 algitex records every LLM interaction.")


@command()
@option("--path", "-p", default=".")
@option("--min-freq", default=3, type=int)
def algo_extract(path: str, min_freq: int):
    """Stage 2: Extract repeating patterns from traces."""
    from algitex.algo import Loop
    loop = Loop(path)
    patterns = loop.extract(min_frequency=min_freq)
    if not patterns:
        console.print("No patterns found yet. Collect more traces first.")
        return
    table = Table(title="Extracted Patterns")
    table.add_column("ID"); table.add_column("Frequency")
    table.add_column("Avg Cost"); table.add_column("Description")
    for p in patterns[:10]:
        table.add_row(p.id, str(p.frequency), f"${p.avg_cost_usd:.4f}", p.description[:60])
    console.print(table)


@command()
@option("--path", "-p", default=".")
@option("--no-llm", is_flag=True)
def algo_rules(path: str, no_llm: bool):
    """Stage 3: Generate deterministic rules for top patterns."""
    from algitex.algo import Loop
    loop = Loop(path)
    with console.status("Generating rules..."):
        rules = loop.generate_rules(use_llm=not no_llm)
    console.print(f"\u2705 Generated {len(rules)} rules")
    for r in rules:
        console.print(f"  {r.pattern_id}: {r.name} ({r.type})")


@command()
@option("--path", "-p", default=".")
def algo_report(path: str):
    """Show algorithmization progress."""
    from algitex.algo import Loop
    report = Loop(path).report()
    console.print(f"\n[bold]Progressive Algorithmization Report[/]")
    console.print(f"Stage: [bold]{report['stage']}[/]")
    console.print(f"Total requests: {report['total_requests']}")
    console.print(f"Deterministic: [green]{report['deterministic_ratio']}[/]")
    console.print(f"Rules active: {report['rules_active']}")
    console.print(f"Cost saved: [green]${report['saved_cost_usd']:.2f}[/]")
