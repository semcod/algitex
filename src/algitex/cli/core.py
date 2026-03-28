"""Core CLI commands for algitex."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def init(path: str = typer.Argument(".", help="Project directory")) -> None:
    """Initialize algitex for a project."""
    project_path = _init_project_dir(path)
    cfg_path = _init_config(project_path)
    
    console.print(f"\n[bold green]\u2705 algitex initialized[/] in {project_path}")
    console.print(f"   Config: {cfg_path}")
    
    _print_tools_status()


def _init_project_dir(path: str) -> Path:
    project_path = Path(path).resolve()
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / ".algitex").mkdir(exist_ok=True)
    return project_path


def _init_config(project_path: Path) -> str:
    from algitex.config import Config
    cfg = Config.load()
    return cfg.save(str(project_path / "algitex.yaml"))


def _print_tools_status():
    from algitex.tools import discover_tools, TOOL_REGISTRY
    tools = discover_tools()
    table = Table(title="Available Tools")
    table.add_column("Tool", style="bold")
    table.add_column("Status")
    table.add_column("Role")
    
    for name, status in tools.items():
        table.add_row(name, str(status), TOOL_REGISTRY.get(name, {}).get("role", "unknown"))
    console.print(table)
    
    missing = [n for n, s in tools.items() if not s.installed]
    if missing:
        console.print(f"\n[yellow]Install missing:[/] pip install {' '.join(missing)}")


def analyze(
    path: str = typer.Option(".", "--path", "-p"),
    quick: bool = typer.Option(False, "--quick", "-q"),
):
    """Analyze project health."""
    from algitex.project import Project
    with console.status("Analyzing..."):
        p = Project(path)
        report = p.analyze(full=not quick)
    console.print(f"\n[bold]Health Report[/]")
    console.print(report.summary())
    if report.grade in ("A", "B"):
        console.print(f"[bold green]Grade {report.grade}[/] — looking good!")
    else:
        console.print(f"[bold yellow]Grade {report.grade}[/] — run [bold]algitex plan[/] for improvements.")


def plan(
    path: str = typer.Option(".", "--path", "-p"),
    sprints: int = typer.Option(2, "--sprints", "-s"),
    focus: str = typer.Option("complexity", "--focus", "-f"),
):
    """Generate sprint plan with auto-tickets."""
    from algitex.project import Project
    with console.status("Planning..."):
        p = Project(path)
        result = p.plan(sprints=sprints, focus=focus)
    console.print(f"\n[bold]Sprint Plan[/]")
    console.print(result["summary"])
    console.print(f"\nTickets created: [bold]{result['tickets_created']}[/]")
    if result["tickets"]:
        table = Table(title="New Tickets")
        table.add_column("ID"); table.add_column("Priority")
        table.add_column("Type"); table.add_column("Title")
        for t in result["tickets"][:15]:
            table.add_row(t["id"], t["priority"], t["type"], t["title"])
        console.print(table)


def go(
    path: str = typer.Option(".", "--path", "-p"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Full pipeline: analyze \u2192 plan \u2192 execute \u2192 validate."""
    from algitex.workflows import Pipeline
    console.print("[bold]Starting full pipeline...[/]\n")
    pipeline = Pipeline(path)
    with console.status("[1/4] Analyzing..."):
        pipeline.analyze()
    console.print("\u2705 Analysis complete")
    with console.status("[2/4] Creating tickets..."):
        pipeline.create_tickets()
    console.print("\u2705 Tickets created")
    if not dry_run:
        with console.status("[3/4] Executing..."):
            pipeline.execute()
        console.print("\u2705 Execution complete")
        with console.status("[4/4] Validating..."):
            pipeline.validate()
        console.print("\u2705 Validation complete")
    result = pipeline.report()
    for step in result["steps"]:
        console.print(f"  {step}")


def status(path: str = typer.Option(".", "--path", "-p")):
    """Show project status dashboard."""
    from algitex.project import Project
    with console.status("Checking status..."):
        p = Project(path)
        s = p.status()

    h = s["health"]
    console.print(f"\n[bold]Project:[/] {s['project']}")
    console.print(
        f"[bold]Health:[/] Grade {h['grade']} | CC\u0304={h['cc_avg']:.1f} | "
        f"vallm={h['vallm_pass_rate']:.0%} | {h['files']} files"
    )
    t = s["tickets"]
    console.print(
        f"[bold]Tickets:[/] {t['open']} open, {t['in_progress']} wip, "
        f"{t['done']} done, {t['blocked']} blocked"
    )
    a = s["algo"]
    console.print(
        f"[bold]Algo:[/] stage={a['stage']} | "
        f"{a['deterministic_ratio']} deterministic | "
        f"{a['rules_active']} rules active | "
        f"saved ${a['saved_cost_usd']:.2f}"
    )
    console.print(
        f"[bold]Cost:[/] ${s['cost_ledger']['total_spent_usd']:.2f} total"
    )


def tools():
    """Show available tools and their status."""
    from algitex.tools import discover_tools, TOOL_REGISTRY
    all_tools = discover_tools()
    table = Table(title="algitex Toolchain")
    table.add_column("Tool", style="bold")
    table.add_column("Installed"); table.add_column("Version")
    table.add_column("CLI"); table.add_column("Role")
    for name, status in all_tools.items():
        table.add_row(
            name,
            "\u2705" if status.installed else "\u274c",
            status.version or "-",
            "\u2705" if status.cli_available else "\u274c",
            TOOL_REGISTRY[name]["role"],
        )
    console.print(table)


def ask(
    prompt: str = typer.Argument(...),
    tier: Optional[str] = typer.Option(None, "--tier", "-t"),
):
    """Quick LLM query via proxym."""
    from algitex.tools.proxy import Proxy
    with console.status("Thinking..."):
        with Proxy() as proxy:
            resp = proxy.ask(prompt, tier=tier)
    console.print(resp.content)
    if resp.model:
        console.print(f"\n[dim]Model: {resp.model} | Cost: ${resp.cost_usd:.4f}[/]")


def sync():
    """Sync tickets to external backend."""
    from algitex.tools.tickets import Tickets
    t = Tickets()
    console.print(f"Sync: {t.sync()}")
