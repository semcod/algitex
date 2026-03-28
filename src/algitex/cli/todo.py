"""Todo subcommands for algitex CLI."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def todo_verify(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
):
    """Verify which TODO tasks are still valid vs already fixed."""
    from algitex.todo import TodoVerifier

    verifier = TodoVerifier(file)
    result = verifier.verify()
    verifier.print_report()


def todo_fix_parallel(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
    workers: int = typer.Option(8, "--workers", "-w", help="Number of parallel workers"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Dry run or actually apply"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter to specific category"),
):
    """Auto-fix mechanical TODO tasks in parallel."""
    from algitex.todo import fix_todos

    result = fix_todos(file, workers=workers, dry_run=dry_run, category=category)
    console.print(f"\n[bold]Results:[/] Fixed: {result['fixed']}, Skipped: {result['skipped']}, Errors: {result['errors']}")


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
        status = "\u23f3" if t.status == "pending" else "\u2705"
        file_disp = t.file_path or "-"
        line_disp = str(t.line_number) if t.line_number else "-"
        table.add_row(t.id, status, file_disp, line_disp, t.description[:60])

    console.print(table)
    console.print(f"\n[bold]{len(tasks)}[/] pending tasks")


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
        status = "[green]\u2713[/]" if r.success else "[red]\u2717[/]"
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
            icon = "\u2713" if r.success else "\u2717"
            color = "green" if r.success else "red"
            console.print(f"[{color}]{icon}[/] {r.task.description[:60]}")
            if r.error:
                console.print(f"   [red]Error: {r.error}[/]")


def todo_benchmark(
    limit: int = typer.Argument(10, help="Number of tasks to benchmark"),
    file: str = typer.Option("TODO.md", "--file", "-f", help="Path to todo file"),
    workers: int = typer.Option(8, "--workers", "-w", help="Number of parallel workers"),
    compare: bool = typer.Option(False, "--compare", "-c", help="Compare parallel vs sequential"),
):
    """Benchmark TODO fix performance."""
    from algitex.todo import benchmark_fix, compare_modes

    if compare:
        compare_modes(file, limit=limit, workers=workers)
    else:
        result = benchmark_fix(file, limit=limit, workers=workers, mode="parallel")
        result.print_report(detailed=True)
        console.print(f"\n[dim]Tip: Use --compare to see parallel vs sequential comparison[/]")


def todo_hybrid(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
    backend: str = typer.Option("litellm-proxy", "--backend", "-b", help="LLM backend: litellm-proxy, ollama, aider"),
    tool: str = typer.Option("aider", "--tool", "-t", help="Tool for LLM fixes: aider, ollama, direct"),
    workers: int = typer.Option(4, "--workers", "-w", help="Parallel workers"),
    rate_limit: int = typer.Option(10, "--rate-limit", "-r", help="LLM calls per second"),
    proxy_url: str = typer.Option("http://localhost:4000", "--proxy-url", "-p", help="LiteLLM proxy URL"),
    hybrid: bool = typer.Option(False, "--hybrid", "-h", help="Add mechanical fixes (default: LLM only)"),
    fallback: bool = typer.Option(True, "--fallback/--no-fallback", help="Enable automatic fallback to alternative backends"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging for debugging"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Preview or execute"),
):
    """Autofix: LLM-based code fixes (use --hybrid for mechanical + LLM)."""
    from algitex.todo import HybridAutofix
    from algitex.tools.logging import set_verbose
    
    # Enable verbose logging if requested
    if verbose:
        set_verbose(True)
        console.print(f"[dim][VERBOSE] Debug logging enabled[/]")

    fixer = HybridAutofix(
        backend=backend,
        tool=tool,
        proxy_url=proxy_url,
        workers=workers,
        rate_limit=rate_limit,
        dry_run=dry_run
    )

    console.print(f"[bold]AutoFix[/]: {file}")
    
    # Show what will be executed
    if hybrid:
        console.print(f"[green]Mode: HYBRID[/] — Phase 1 (mechanical) + Phase 2 (LLM)")
        console.print(f"   • Phase 1: Parallel mechanical fixes (workers={workers})")
        console.print(f"   • Phase 2: LLM-based fixes via {backend} (rate={rate_limit}/sec)")
    else:
        console.print(f"[yellow]Mode: LLM ONLY[/] — Skipping mechanical fixes")
        console.print(f"   • LLM fixes via {backend} (rate={rate_limit}/sec)")
    
    if fallback:
        console.print(f"   • Fallback: ENABLED (auto-switch to ollama/aider if {backend} fails)")
    else:
        console.print(f"   • Fallback: DISABLED")
    
    if verbose:
        console.print(f"   • Verbose: ENABLED (detailed function call logging)")
    
    if dry_run:
        console.print(f"\n[dim]⚠️  DRY RUN — No changes will be made. Use --execute to apply fixes.[/]")
    else:
        console.print(f"\n[bold red]⚡ EXECUTE — Fixes will be applied to source files and TODO.md will be updated.[/]")
    
    console.print(f"\nBackend: {backend}, Tool: {tool}, Proxy: {proxy_url}")
    console.print(f"Workers: {workers}, Rate: {rate_limit}/sec\n")

    if hybrid:
        result = fixer.fix_all(file)
    else:
        result = fixer.fix_complex(file)
    fixer.print_summary(result)


