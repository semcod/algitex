"""CLI — the algitex command.

Usage:
    algitex init ./my-app           # initialize
    algitex analyze                 # run all analysis
    algitex plan                    # generate sprint plan
    algitex go                      # full pipeline
    algitex status                  # dashboard

    algitex ask "question"          # quick LLM query
    algitex ticket add "title"      # add ticket
    algitex ticket list             # show tickets
    algitex sync                    # push to GitHub/Jira

    algitex algo discover           # start trace collection
    algitex algo extract            # find patterns
    algitex algo rules              # generate deterministic replacements
    algitex algo report             # show progress

    algitex workflow run f.md       # execute Propact workflow
    algitex workflow validate f.md  # check syntax
    algitex tools                   # show installed tools
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="algitex",
    help="Progressive algorithmization toolchain — from LLM to deterministic, from proxy to tickets.",
    no_args_is_help=True,
)
ticket_app = typer.Typer(help="Manage tickets.")
algo_app = typer.Typer(help="Progressive algorithmization.")
workflow_app = typer.Typer(help="Propact Markdown workflows.")
docker_app = typer.Typer(help="Manage Docker-based development tools.")
app.add_typer(ticket_app, name="ticket")
app.add_typer(algo_app, name="algo")
app.add_typer(workflow_app, name="workflow")
app.add_typer(docker_app, name="docker")

# ── Todo subcommands ───────────────────────────────────

todo_app = typer.Typer(help="Execute todo lists via Docker MCP.")
app.add_typer(todo_app, name="todo")

console = Console()


@app.command()
def init(path: str = typer.Argument(".", help="Project directory")) -> None:
    """Initialize algitex for a project."""
    from algitex.config import Config
    from algitex.tools import discover_tools

    project_path = Path(path).resolve()
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / ".algitex").mkdir(exist_ok=True)

    cfg = Config.load()
    cfg_path = cfg.save(str(project_path / "algitex.yaml"))

    console.print(f"\n[bold green]\u2705 algitex initialized[/] in {project_path}")
    console.print(f"   Config: {cfg_path}")

    tools = discover_tools()
    table = Table(title="Available Tools")
    table.add_column("Tool", style="bold")
    table.add_column("Status")
    table.add_column("Role")
    from algitex.tools import TOOL_REGISTRY
    for name, status in tools.items():
        table.add_row(name, str(status), TOOL_REGISTRY[name]["role"])
    console.print(table)

    missing = [n for n, s in tools.items() if not s.installed]
    if missing:
        console.print(f"\n[yellow]Install missing:[/] pip install {' '.join(missing)}")


@app.command()
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


@app.command()
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


@app.command()
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


@app.command()
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


@app.command()
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


@app.command()
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


@app.command()
def sync():
    """Sync tickets to external backend."""
    from algitex.tools.tickets import Tickets
    t = Tickets()
    console.print(f"Sync: {t.sync()}")


# ── Ticket subcommands ───────────────────────────────────

@ticket_app.command("add")
def ticket_add(
    title: str = typer.Argument(...),
    priority: str = typer.Option("normal", "--priority", "-p"),
    type: str = typer.Option("task", "--type", "-t"),
):
    """Add a new ticket."""
    from algitex.tools.tickets import Tickets
    ticket = Tickets().add(title, priority=priority, type=type)
    console.print(f"\u2705 Created: [bold]{ticket.id}[/] \u2014 {ticket.title}")


@ticket_app.command("list")
def ticket_list(status: Optional[str] = typer.Option(None, "--status", "-s")):
    """List tickets."""
    from algitex.tools.tickets import Tickets
    tickets = Tickets().list(status=status)
    if not tickets:
        console.print("No tickets."); return
    table = Table(title="Tickets")
    table.add_column("ID"); table.add_column("Status")
    table.add_column("Priority"); table.add_column("Type"); table.add_column("Title")
    for t in tickets:
        table.add_row(t.id, t.status, t.priority, t.type, t.title)
    console.print(table)


@ticket_app.command("board")
def ticket_board():
    """Kanban board view."""
    from algitex.tools.tickets import Tickets
    for col, tickets in Tickets().board().items():
        if tickets:
            console.print(f"\n[bold]{col.upper()}[/] ({len(tickets)})")
            for t in tickets:
                console.print(f"  [{t.priority}] {t.id}: {t.title}")


# ── Algo subcommands ─────────────────────────────────────

@algo_app.command("discover")
def algo_discover(path: str = typer.Option(".", "--path", "-p")):
    """Stage 1: Start trace collection from proxym."""
    from algitex.algo import Loop
    loop = Loop(path)
    loop.discover()
    console.print("\u2705 Discovery mode active. Traces will be collected from proxym.")
    console.print("Use your IDE normally \u2014 algitex records every LLM interaction.")


@algo_app.command("extract")
def algo_extract(
    path: str = typer.Option(".", "--path", "-p"),
    min_freq: int = typer.Option(3, "--min-freq"),
):
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


@algo_app.command("rules")
def algo_rules(
    path: str = typer.Option(".", "--path", "-p"),
    no_llm: bool = typer.Option(False, "--no-llm"),
):
    """Stage 3: Generate deterministic rules for top patterns."""
    from algitex.algo import Loop
    loop = Loop(path)
    with console.status("Generating rules..."):
        rules = loop.generate_rules(use_llm=not no_llm)
    console.print(f"\u2705 Generated {len(rules)} rules")
    for r in rules:
        console.print(f"  {r.pattern_id}: {r.name} ({r.type})")


@algo_app.command("report")
def algo_report(path: str = typer.Option(".", "--path", "-p")):
    """Show algorithmization progress."""
    from algitex.algo import Loop
    report = Loop(path).report()
    console.print(f"\n[bold]Progressive Algorithmization Report[/]")
    console.print(f"Stage: [bold]{report['stage']}[/]")
    console.print(f"Total requests: {report['total_requests']}")
    console.print(f"Deterministic: [green]{report['deterministic_ratio']}[/]")
    console.print(f"Rules active: {report['rules_active']}")
    console.print(f"Cost saved: [green]${report['saved_cost_usd']:.2f}[/]")


# ── Workflow subcommands ─────────────────────────────────

@workflow_app.command("run")
def workflow_run(
    path: str = typer.Argument(..., help="Path to .md workflow"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Execute a Propact Markdown workflow."""
    from algitex.project import Project
    p = Project(".")
    with console.status(f"Running workflow {path}..."):
        result = p.run_workflow(path, dry_run=dry_run)
    if result["success"]:
        console.print(f"\u2705 Workflow complete: {result['steps_done']} steps, ${result['total_cost_usd']:.4f}")
    else:
        console.print(f"\u274c Workflow failed: {result.get('steps_failed', 0)} steps failed")
        for err in result.get("errors", []):
            console.print(f"  {err}")


@workflow_app.command("validate")
def workflow_validate(path: str = typer.Argument(...)):
    """Check a Propact workflow for errors."""
    from algitex.propact import Workflow
    wf = Workflow(path)
    errors = wf.validate()
    if errors:
        console.print(f"\u274c {len(errors)} errors:")
        for e in errors:
            console.print(f"  {e}")
    else:
        steps = wf.parse()
        console.print(f"\u2705 Valid workflow: {len(steps)} steps")


# ── Docker subcommands ───────────────────────────────────

@docker_app.command("list")
def docker_list():
    """List available Docker tools from docker-tools.yaml."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config
    
    mgr = DockerToolManager(Config.load())
    running = mgr.list_running()
    
    table = Table(title="Docker Tools")
    table.add_column("Status", style="bold")
    table.add_column("Tool", style="bold")
    table.add_column("Transport")
    table.add_column("Image")
    
    for name in mgr.list_tools():
        tool = mgr._tools[name]
        status = "\u25cf" if name in running else "\u25cb"
        table.add_row(status, name, tool.transport, tool.image)
    console.print(table)


@docker_app.command("spawn")
def docker_spawn(tool_name: str = typer.Argument(...)):
    """Start a Docker tool container."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config
    
    mgr = DockerToolManager(Config.load())
    try:
        rt = mgr.spawn(tool_name)
        console.print(f"  \u25cf {tool_name} → {rt.container_id}")
        if rt.endpoint:
            console.print(f"  Endpoint: {rt.endpoint}")
    except Exception as e:
        console.print(f"\u274c Failed to spawn {tool_name}: {e}")


@docker_app.command("call")
def docker_call(
    tool_name: str = typer.Argument(...),
    action: str = typer.Argument(...),
    input_json: Optional[str] = typer.Option(None, "--input", "-i", help="JSON input")
):
    """Call an MCP tool on a running Docker container."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config
    import json
    
    mgr = DockerToolManager(Config.load())
    args = json.loads(input_json) if input_json else {}
    
    try:
        result = mgr.call_tool(tool_name, action, args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"\u274c Failed to call {tool_name}.{action}: {e}")


@docker_app.command("teardown")
def docker_teardown(tool_name: Optional[str] = typer.Argument(None)):
    """Stop Docker tool containers."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config
    
    mgr = DockerToolManager(Config.load())
    if tool_name:
        mgr.teardown(tool_name)
        console.print(f"  \u25cb {tool_name} stopped")
    else:
        mgr.teardown_all()
        console.print("  \u25cb All tools stopped")


@docker_app.command("caps")
def docker_caps(tool_name: str = typer.Argument(...)):
    """List MCP capabilities of a Docker tool."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config
    
    mgr = DockerToolManager(Config.load())
    
    if tool_name not in mgr.list_running():
        console.print(f"Spawning {tool_name} to check capabilities...")
        mgr.spawn(tool_name)
    
    for cap in mgr.get_capabilities(tool_name):
        console.print(f"  → {cap}")


# ── Todo subcommands ───────────────────────────────────

@todo_app.command("list")
def todo_list(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
):
    """Parse and display todo tasks from a file."""
    from algitex.tools.todo_parser import TodoParser

    parser = TodoParser(file)
    tasks = parser.parse()

    if not tasks:
        console.print(f"[yellow]No pending tasks found in {file}[/]")
        return

    table = Table(title=f"Todo Tasks: {file}")
    table.add_column("ID", style="bold")
    table.add_column("Status", style="dim")
    table.add_column("File", style="cyan")
    table.add_column("Line", style="dim")
    table.add_column("Description")

    for t in tasks:
        status = "⏳" if t.status == "pending" else "✅"
        file_disp = t.file_path or "-"
        line_disp = str(t.line_number) if t.line_number else "-"
        table.add_row(t.id, status, file_disp, line_disp, t.description[:60])

    console.print(table)
    console.print(f"\n[bold]{len(tasks)}[/] pending tasks")


@todo_app.command("run")
def todo_run(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
    tool: str = typer.Option("local", "--tool", "-t", help="Tool to use (local, filesystem-mcp, aider-mcp)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
    limit: int = typer.Option(0, "--limit", "-l", help="Limit number of tasks (0 = all)"),
):
    """Execute todo tasks via Docker MCP."""
    from algitex.tools.todo_runner import TodoRunner

    runner = TodoRunner(".")
    results = runner.run_from_file(file, tool=tool, dry_run=dry_run, limit=limit)

    if not results:
        console.print(f"[yellow]No pending tasks in {file}[/]")
        return

    # Display results
    table = Table(title=f"Execution Results ({tool})")
    table.add_column("Task", style="bold")
    table.add_column("Status")
    table.add_column("Action")
    table.add_column("Output", max_width=50)

    for r in results:
        status = "[green]✓[/]" if r.success else "[red]✗[/]"
        output = r.output[:100] + "..." if len(r.output) > 100 else r.output
        if r.error:
            output = f"[red]{r.error[:50]}[/]"
        table.add_row(r.task.id, status, r.action, output or "-")

    console.print(table)

    # Summary
    summary = runner.get_summary()
    console.print(f"\n[bold]Summary:[/] {summary['success']}/{summary['total']} tasks completed")
    if summary['failed'] > 0:
        console.print(f"[red]{summary['failed']} tasks failed[/]")


@todo_app.command("fix")
def todo_fix(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
    tool: str = typer.Option("ollama-mcp", "--tool", "-t", help="Tool to use (local, ollama-mcp, filesystem-mcp, aider-mcp, nap)"),
    task_id: Optional[str] = typer.Option(None, "--task", help="Specific task ID to fix"),
    limit: int = typer.Option(0, "--limit", "-l", help="Limit number of tasks (0 = all)"),
):
    """Execute fix tasks (prefact-style) via Docker MCP."""
    from algitex.tools.todo_parser import TodoParser
    from algitex.tools.todo_runner import TodoRunner

    parser = TodoParser(file)
    all_tasks = parser.parse()

    # Filter to fix-related tasks
    fix_keywords = ["fix", "repair", "correct", "missing", "unused", "magic number", "return type"]
    fix_tasks = [t for t in all_tasks if any(kw in t.description.lower() for kw in fix_keywords)]

    if task_id:
        fix_tasks = [t for t in fix_tasks if t.id == task_id]

    if not fix_tasks:
        console.print("[yellow]No fix tasks found[/]")
        return

    if limit > 0:
        fix_tasks = fix_tasks[:limit]

    console.print(f"[bold]Found {len(fix_tasks)} fix tasks[/]\n")

    with TodoRunner(".") as runner:
        results = runner.run(fix_tasks, tool=tool)

        for r in results:
            icon = "✓" if r.success else "✗"
            color = "green" if r.success else "red"
            console.print(f"[{color}]{icon}[/] {r.task.description[:60]}")
            if r.error:
                console.print(f"   [red]Error: {r.error}[/]")


if __name__ == "__main__":
    app()
