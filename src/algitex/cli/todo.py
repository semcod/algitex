"""Todo subcommands for algitex CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _render_todo_stats(file: str, tasks) -> None:
    """Render tier and category stats for a TODO file."""
    from algitex.todo import summarize_tasks

    summary = summarize_tasks(tasks)

    tier_table = Table(title=f"TODO Stats: {file}")
    tier_table.add_column("Tier", style="bold")
    tier_table.add_column("Count", justify="right")
    tier_table.add_column("Share", justify="right")
    for tier, label in (("algorithm", "Algorithm"), ("micro", "Small LLM"), ("big", "Big LLM")):
        count = summary.tier_counts.get(tier, 0)
        share = f"{summary.tier_percent(tier)}%"
        tier_table.add_row(label, str(count), share)

    console.print(tier_table)

    category_table = Table(title="Top Categories")
    category_table.add_column("Category", style="bold")
    category_table.add_column("Count", justify="right")
    for category, count in summary.top_categories(limit=12):
        category_table.add_row(category, str(count))

    console.print(category_table)
    console.print(
        f"\n[bold]Total:[/] {summary.total} | "
        f"Algorithm: {summary.algorithmic} | Micro: {summary.micro} | Big: {summary.big}"
    )


def _run_with_dashboard(
    file: str,
    tasks: list,
    algo: bool,
    micro: bool,
    all_phases: bool,
    workers: int,
    micro_workers: int,
    model: str,
    backend: str,
    rate_limit: int,
    proxy_url: str,
    dry_run: bool,
) -> None:
    """Run todo fix with live dashboard."""
    from algitex.dashboard import LiveDashboard
    from algitex.todo import (
        BIG_CATEGORIES,
        HybridAutofix,
        MicroFixer,
        classify_task,
        mark_tasks_completed,
        parallel_fix_and_update,
    )
    from algitex.tools.ollama_cache import LLMCache
    import threading
    import time

    # Prepare tasks by tier
    algo_tasks = [t for t in tasks if classify_task(t).tier == "algorithm"]
    micro_tasks = [t for t in tasks if classify_task(t).tier == "micro"]
    big_tasks = [t for t in tasks if classify_task(t).tier == "big"] if all_phases else []

    # Initialize dashboard
    dashboard = LiveDashboard(refresh_rate=1.0)
    
    # Initialize tier states
    if algo:
        dashboard.update_tier_progress("algorithm", total=len(algo_tasks), active=True)
    if micro:
        dashboard.update_tier_progress("micro", total=len(micro_tasks), active=True)
    if all_phases and big_tasks:
        dashboard.update_tier_progress("big", total=len(big_tasks), active=True)

    # Initialize cache stats
    cache = LLMCache(".algitex/cache")
    cache_stats = cache.stats()
    dashboard.update_cache_stats(
        hits=cache_stats["hits"],
        misses=cache_stats["misses"],
        entries=cache_stats["entries"],
        size_bytes=cache_stats["size_bytes"],
    )

    results = []

    def run_phases():
        """Run all phases and update dashboard."""
        nonlocal results

        # Phase 1: Algorithm
        if algo and algo_tasks:
            dashboard.update_tier_progress("algorithm", current=0, active=True)
            
            # Run with periodic updates
            batch_size = max(1, len(algo_tasks) // 10)
            for i in range(0, len(algo_tasks), batch_size):
                batch = algo_tasks[i:i+batch_size]
                result = parallel_fix_and_update(file, workers=workers, dry_run=dry_run, tasks=batch)
                dashboard.update_tier_progress(
                    "algorithm",
                    current=min(i + batch_size, len(algo_tasks)),
                    success=sum(r.get("success", 0) for r in results if isinstance(r, dict)),
                )
                results.append(result)
            
            dashboard.update_tier_progress("algorithm", active=False)

        # Phase 2: Micro
        if micro and micro_tasks:
            dashboard.update_tier_progress("micro", current=0, active=True)
            
            micro_fixer = MicroFixer(
                ollama_url="http://localhost:11434",
                model=model,
                workers=micro_workers,
                dry_run=dry_run,
            )
            
            # Update cache stats periodically
            def update_cache():
                while dashboard._running:
                    stats = cache.stats()
                    dashboard.update_cache_stats(
                        hits=stats["hits"],
                        misses=stats["misses"],
                        entries=stats["entries"],
                        size_bytes=stats["size_bytes"],
                    )
                    time.sleep(2)
            
            cache_thread = threading.Thread(target=update_cache, daemon=True)
            cache_thread.start()
            
            micro_results = micro_fixer.fix_tasks_detailed(micro_tasks)
            result = {
                "fixed": sum(1 for item in micro_results if item.success),
                "skipped": sum(1 for item in micro_results if not item.success and not item.error),
                "errors": sum(1 for item in micro_results if item.error),
            }
            results.append(("Small LLM", result))
            
            dashboard.update_tier_progress(
                "micro",
                current=len(micro_tasks),
                success=result["fixed"],
                failed=result["errors"],
                active=False,
            )
            
            if not dry_run and result.get("fixed", 0) > 0:
                completed_ids = {item.task_id for item in micro_results if item.success}
                completed_tasks = [
                    task for task in micro_tasks if f"{task.file}:{task.line}" in completed_ids
                ]
                if completed_tasks:
                    mark_tasks_completed(file, completed_tasks)

        # Phase 3: Big
        if all_phases and big_tasks:
            dashboard.update_tier_progress("big", current=0, active=True)
            
            fixer = HybridAutofix(
                backend=backend,
                tool="ollama-mcp",
                proxy_url=proxy_url,
                workers=workers,
                rate_limit=rate_limit,
                dry_run=dry_run,
            )
            
            # Simulate progress (HybridAutofix doesn't expose per-task progress)
            dashboard.update_tier_progress("big", current=len(big_tasks) // 2)
            
            result = fixer.fix_complex(file, include_categories=set(BIG_CATEGORIES), tasks=big_tasks)
            results.append(("Big LLM", result))
            
            dashboard.update_tier_progress(
                "big",
                current=len(big_tasks),
                success=result.get("fixed", 0),
                active=False,
            )
            
            if not dry_run and result.get("fixed", 0) == len(big_tasks) and big_tasks:
                mark_tasks_completed(file, big_tasks)

    # Run with dashboard
    try:
        dashboard.start()
        run_phases()
        
        # Show final summary
        console.print("\n[bold]Tiered Summary[/]")
        for phase, result in results:
            if isinstance(result, dict):
                console.print(
                    f"  • {phase}: fixed={result.get('fixed', 0)}, skipped={result.get('skipped', 0)}, errors={result.get('errors', 0)}"
                )
        
        time.sleep(1)  # Let user see final state
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation interrupted by user[/]")
    finally:
        dashboard.stop()


def todo_stats(
    file: str = typer.Argument("TODO.md", help="Path to todo file"),
):
    """Show tier and category stats for a TODO file."""
    from algitex.todo import parse_todo

    try:
        tasks = parse_todo(file)
    except FileNotFoundError:
        console.print(f"[red]TODO file not found:[/] {file}")
        return

    if not tasks:
        console.print(f"[yellow]No pending tasks found in {file}[/]")
        return

    _render_todo_stats(file, tasks)


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
    dry_run: bool = typer.Option(False, "--dry-run/--execute", help="Preview without executing"),
    algo: bool = typer.Option(False, "--algo", help="Run only algorithmic fixes"),
    micro: bool = typer.Option(False, "--micro", "--small-llm", help="Run only small LLM micro-fixes"),
    all_phases: bool = typer.Option(False, "--all", help="Run algorithmic, small LLM, and big LLM phases"),
    dashboard: bool = typer.Option(False, "--dashboard", "-d", help="Show live dashboard during execution"),
    workers: int = typer.Option(8, "--workers", "-w", help="Workers for algorithmic and big LLM phases"),
    micro_workers: int = typer.Option(4, "--micro-workers", help="Workers for the small LLM phase"),
    model: str = typer.Option("qwen2.5-coder:7b", "--model", help="Ollama model for the small LLM phase"),
    backend: str = typer.Option("ollama", "--backend", "-b", help="Backend for the big LLM phase"),
    rate_limit: int = typer.Option(10, "--rate-limit", "-r", help="LLM calls per second for the big LLM phase"),
    proxy_url: str = typer.Option("http://localhost:4000", "--proxy-url", "-p", help="LiteLLM proxy URL"),
):
    """Execute fix tasks (prefact-style) via Docker MCP.
    
    5-step pipeline: parse → classify → execute → validate → report.
    CC: 8 (5 functions + 3 branches)
    Was: CC ~50 (nested phase logic)
    """
    # Step 1: Parse and filter tasks
    tasks = _tf_parse_and_filter(file, task_id, limit)
    if not tasks:
        console.print("[yellow]No fix tasks found[/]")
        return

    console.print(f"[bold]Tiered AutoFix[/]: {file}")
    _render_todo_stats(file, tasks)

    # Check if using phased execution
    if algo or micro or all_phases:
        if dashboard:
            _run_with_dashboard(file, tasks, algo, micro, all_phases, workers, micro_workers, model, backend, rate_limit, proxy_url, dry_run)
            return

        # Step 2: Classify tasks by tier
        classified = _tf_classify_tasks(tasks)

        # Step 3: Execute fixes per tier
        results = _tf_execute_phased(
            file, classified, algo, micro, all_phases,
            workers, micro_workers, model, backend, rate_limit, proxy_url, dry_run
        )

        # Step 4: Validate results
        report = _tf_validate_results(results)

        # Step 5: Print report
        _tf_print_report(report)
        return

    # Legacy path: non-tiered execution
    _tf_run_legacy(file, tasks, tool, dry_run)


def _tf_parse_and_filter(file: str, task_id: str | None, limit: int) -> list:
    """Step 1: Parse TODO.md and filter by task_id and limit.
    
    CC: 3 (parse + filter + limit)
    """
    from algitex.todo import parse_todo

    try:
        tasks = parse_todo(file)
    except FileNotFoundError:
        console.print(f"[red]TODO file not found:[/] {file}")
        return []

    if task_id:
        tasks = [t for t in tasks if f"{t.file}:{t.line}" == task_id]

    if limit > 0:
        tasks = tasks[:limit]

    return tasks


def _tf_classify_tasks(tasks: list) -> dict[str, list]:
    """Step 2: Group tasks by execution tier.
    
    CC: 3 (dict lookup + 2 list comps)
    """
    from algitex.todo import classify_task

    return {
        "algorithm": [t for t in tasks if classify_task(t).tier == "algorithm"],
        "micro": [t for t in tasks if classify_task(t).tier == "micro"],
        "big": [t for t in tasks if classify_task(t).tier == "big"],
    }


def _tf_execute_phased(
    file: str,
    classified: dict[str, list],
    algo: bool,
    micro: bool,
    all_phases: bool,
    workers: int,
    micro_workers: int,
    model: str,
    backend: str,
    rate_limit: int,
    proxy_url: str,
    dry_run: bool,
) -> list[tuple[str, dict]]:
    """Step 3: Execute fixes per tier.
    
    CC: 5 (3 phase handlers + 2 conditionals)
    """
    from algitex.todo import (
        BIG_CATEGORIES,
        HybridAutofix,
        MicroFixer,
        mark_tasks_completed,
        parallel_fix_and_update,
    )

    results: list[tuple[str, dict]] = []

    if all_phases:
        algo = True
        micro = True

    # Phase 1: Algorithm
    if algo and classified["algorithm"]:
        algo_tasks = classified["algorithm"]
        console.print(f"\n[green]Phase 1: Algorithm[/] — {len(algo_tasks)} tasks")
        result = parallel_fix_and_update(file, workers=workers, dry_run=dry_run, tasks=algo_tasks)
        results.append(("Algorithm", result))

    # Phase 2: Small LLM
    if micro and classified["micro"]:
        micro_tasks = classified["micro"]
        console.print(f"\n[cyan]Phase 2: Small LLM[/] — {len(micro_tasks)} tasks")
        micro_fixer = MicroFixer(
            ollama_url="http://localhost:11434",
            model=model,
            workers=micro_workers,
            dry_run=dry_run,
        )
        micro_results = micro_fixer.fix_tasks_detailed(micro_tasks)
        result = {
            "fixed": sum(1 for item in micro_results if item.success),
            "skipped": sum(1 for item in micro_results if not item.success and not item.error),
            "errors": sum(1 for item in micro_results if item.error),
        }
        results.append(("Small LLM", result))

        if not dry_run and result.get("fixed", 0) > 0:
            completed_ids = {item.task_id for item in micro_results if item.success}
            completed_tasks = [t for t in micro_tasks if f"{t.file}:{t.line}" in completed_ids]
            if completed_tasks:
                mark_tasks_completed(file, completed_tasks)

    # Phase 3: Big LLM
    if all_phases and classified["big"]:
        big_tasks = classified["big"]
        console.print(f"\n[magenta]Phase 3: Big LLM[/] — {len(big_tasks)} tasks")
        fixer = HybridAutofix(
            backend=backend,
            tool="ollama-mcp",
            proxy_url=proxy_url,
            workers=workers,
            rate_limit=rate_limit,
            dry_run=dry_run,
        )
        result = fixer.fix_complex(file, include_categories=set(BIG_CATEGORIES), tasks=big_tasks)
        results.append(("Big LLM", result))

        if not dry_run and result.get("fixed", 0) == len(big_tasks) and big_tasks:
            mark_tasks_completed(file, big_tasks)

    return results


def _tf_validate_results(results: list[tuple[str, dict]]) -> dict:
    """Step 4: Aggregate fix results into report.
    
    CC: 2 (sum aggregation)
    """
    return {
        "phases": [name for name, _ in results],
        "fixed": sum(r.get("fixed", 0) for _, r in results),
        "skipped": sum(r.get("skipped", 0) for _, r in results),
        "errors": sum(r.get("errors", 0) for _, r in results),
        "details": results,
    }


def _tf_print_report(report: dict) -> None:
    """Step 5: Print human-readable report.
    
    CC: 2 (header + details)
    """
    console.print(f"\n[bold]Tiered Summary[/]")
    for phase, result in report.get("details", []):
        console.print(
            f"  • {phase}: fixed={result.get('fixed', 0)}, "
            f"skipped={result.get('skipped', 0)}, errors={result.get('errors', 0)}"
        )


def _tf_run_legacy(file: str, tasks: list, tool: str, dry_run: bool) -> None:
    """Legacy non-tiered execution path.
    
    Kept for backward compatibility.
    """
    from algitex.tools.todo_parser import TodoParser
    from algitex.tools.todo_runner import TodoRunner

    parser = TodoParser(file)
    all_tasks = parser.parse()

    # Filter to fix-related tasks
    fix_keywords = ["fix", "repair", "correct", "missing", "unused", "magic number", "return type"]
    fix_tasks = [t for t in all_tasks if any(kw in t.description.lower() for kw in fix_keywords)]

    if not fix_tasks:
        console.print("[yellow]No fix tasks found[/]")
        return

    console.print(f"[bold]Found {len(fix_tasks)} fix tasks[/]\n")

    with TodoRunner(".") as runner:
        results = runner.run(fix_tasks, tool=tool, dry_run=dry_run)

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
    dashboard: bool = typer.Option(False, "--dashboard", "-d", help="Show live dashboard during execution"),
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

    if dashboard:
        # Run with live dashboard
        _run_hybrid_with_dashboard(file, fixer, hybrid, dry_run)
        return

    if hybrid:
        result = fixer.fix_all(file)
    else:
        result = fixer.fix_complex(file)
    
    # Update TODO.md - mark completed tasks
    if not dry_run and result.get('fixed', 0) > 0:
        from algitex.todo.fixer import parse_todo, mark_tasks_completed
        try:
            tasks = parse_todo(file)
            # Mark LLM tasks as completed (categories not in FIXERS)
            from algitex.todo.fixer import FIXERS
            llm_tasks = [t for t in tasks if t.category not in FIXERS]
            task_ids = [f"{t.file}:{t.line}" for t in llm_tasks]
            if task_ids:
                mark_tasks_completed(file, task_ids)
                console.print(f"\n[green]✓ Updated TODO.md — marked {len(task_ids)} tasks as completed[/]")
        except Exception as e:
            console.print(f"\n[yellow]⚠️  Could not update TODO.md: {e}[/]")
    
    fixer.print_summary(result)


def todo_batch(
    file: Path = typer.Option(Path("TODO.md"), "--file", "-f", help="TODO.md file path"),
    backend: str = typer.Option("ollama", "--backend", "-b", help="Backend: ollama, litellm-proxy"),
    model: str = typer.Option("qwen3:8b", "--model", "-m", help="Ollama model name (e.g., qwen3:8b, qwen2.5-coder:7b)"),
    batch_size: int = typer.Option(5, "--batch-size", "-s", help="Max files per batch"),
    parallel: int = typer.Option(3, "--parallel", "-p", help="Parallel groups (default: 3)"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Dry run or execute"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
    prune: bool = typer.Option(False, "--prune", help="Remove outdated tasks from TODO.md before batch"),
    limit: int = typer.Option(0, "--limit", "-l", help="Limit number of tasks (0 = all)"),
    no_log: bool = typer.Option(False, "--no-log", help="Disable markdown logging"),
    dashboard: bool = typer.Option(False, "--dashboard", "-d", help="Show live dashboard during execution"),
):
    """BatchFix: grupowanie i optymalizacja podobnych zadań.
    
    Zamiast wykonywać każde zadanie osobno, BatchFix grupuje podobne problemy
    (np. "f-string", "magic number") i wykonuje je za jednym razem.
    
    Przykłady:
        algitex todo batch --dry-run              # Symulacja
        algitex todo batch --execute             # Wykonaj fixy
        algitex todo batch -b ollama -s 3        # Ollama, max 3 pliki/batch
        algitex todo batch --execute --prune     # Wyczyść nieaktualne zadania
        algitex todo batch --execute --no-log   # Wyłącz logowanie markdown
    """
    from algitex.todo import parse_todo
    from algitex.tools.autofix.batch_backend import BatchFixBackend, Task
    from algitex.tools.logging import set_verbose
    
    if verbose:
        set_verbose(True)
        console.print("[dim][VERBOSE] Debug logging enabled[/]")
    
    console.print(f"[bold]BatchFix[/]: {file}")
    console.print(f"Backend: {backend}, Batch size: {batch_size}, Parallel: {parallel}")
    
    if dry_run:
        console.print(f"\n[dim]⚠️  DRY RUN — Symulacja bez zmian[/]")
    else:
        console.print(f"\n[bold red]⚡ EXECUTE — Fixy zostaną zastosowane[/]")
    
    # Prune outdated tasks if requested
    if prune:
        console.print(f"\n[bold]🧹 Prune: Czyszczę nieaktualne zadania z {file}...[/]")
        # Call the verify-prefact logic with prune
        from algitex.cli.todo import todo_verify_prefact
        todo_verify_prefact(file=str(file), prune=True)
        console.print(f"[dim]Prune zakończony. Kontynuuję batch...[/]\n")
    
    # Parse TODO
    todo_tasks = parse_todo(file)
    
    # Apply limit if specified
    if limit > 0:
        todo_tasks = todo_tasks[:limit]
        console.print(f"[dim]Limit: Przetwarzam tylko pierwsze {limit} zadań[/]")
    
    # Convert to Task objects
    tasks = [
        Task(
            id=f"{t.file}:{t.line}",
            description=t.message,
            file_path=str(t.file),
            line_number=t.line,
            status="pending"
        )
        for t in todo_tasks
    ]
    
    console.print(f"\n📋 Znaleziono {len(tasks)} zadań")
    
    if not tasks:
        console.print("[yellow]Brak zadań do wykonania[/]")
        return
    
    # Initialize backend
    backend_fixer = BatchFixBackend(
        base_url="http://localhost:11434",
        model=model,
        dry_run=dry_run,
        enable_logging=not no_log
    )
    backend_fixer.MAX_FILES_PER_BATCH = batch_size
    
    # Execute batch fix with parallel groups
    results = backend_fixer.fix_batch(tasks, max_parallel=parallel)
    
    # Summary
    success = sum(1 for r in results if r.success)
    failed = len(results) - success
    
    console.print(f"\n[bold]{'═' * 60}[/]")
    console.print(f"  BATCH FIX SUMMARY")
    console.print(f"[bold]{'═' * 60}[/]")
    console.print(f"\n  ✅ Success: {success}")
    console.print(f"  ❌ Failed:  {failed}")
    console.print(f"  📊 Total:   {len(results)}")
    
    if not dry_run and success > 0:
        console.print(f"\n[green]✓ Zaktualizowano {success} plików[/]")
        # TODO: Mark tasks as completed in TODO.md
    
    console.print(f"[bold]{'═' * 60}[/]")


def todo_verify_prefact(
    file: str = typer.Option("TODO.md", "--file", "-f", help="Path to TODO.md"),
    prune: bool = typer.Option(False, "--prune", "-p", help="Remove outdated tasks from TODO.md"),
):
    """Verify TODO.md against actual code using prefact.
    
    Uses prefact to scan for issues and compares with TODO.md.
    Shows which tasks are still valid and which are outdated.
    
    With --prune: removes outdated tasks from TODO.md
    """
    from pathlib import Path
    import subprocess
    import re
    import tempfile
    
    console.print(f"[bold]Verify TODO.md with prefact[/]: {file}")
    
    # Run prefact scan
    console.print("\n🔍 Running prefact scan...")
    try:
        result = subprocess.run(
            ["prefact", "scan", "--format", "json"],
            capture_output=True,
            text=True,
            cwd="."
        )
        if result.returncode != 0:
            console.print(f"[yellow]⚠️  Prefact scan failed: {result.stderr}[/]")
            return
    except FileNotFoundError:
        console.print("[red]✗ prefact not installed. Install with: pip install prefact[/]")
        return
    
    # Parse current TODO.md
    todo_path = Path(file)
    if not todo_path.exists():
        console.print(f"[red]✗ {file} not found[/]")
        return
    
    todo_content = todo_path.read_text()
    todo_tasks = []
    
    for line in todo_content.splitlines():
        match = re.match(r"- \[([ x])\] (.+):(\d+) - (.+)", line)
        if match:
            status, filepath, lineno, message = match.groups()
            todo_tasks.append({
                "status": status,
                "file": filepath,
                "line": int(lineno),
                "message": message,
                "original_line": line
            })
    
    console.print(f"📋 Found {len(todo_tasks)} tasks in TODO.md")
    
    # Simple validation: check if files/lines still exist
    valid_tasks = []
    outdated_tasks = []
    
    for task in todo_tasks:
        filepath = task["file"]
        try:
            path = Path(filepath)
            if not path.exists():
                outdated_tasks.append(task)
                continue
            
            # Check if line still exists
            lines = path.read_text().splitlines()
            line_no = task["line"] - 1
            
            if line_no >= len(lines):
                outdated_tasks.append(task)
                continue
            
            # Check if the issue keywords are still in the line
            line_content = lines[line_no] if line_no < len(lines) else ""
            
            # Heuristics for different issue types
            is_valid = True
            msg_lower = task["message"].lower()
            
            if "unused" in msg_lower and "import" in msg_lower:
                # Check if import is still in the line
                if "import" not in line_content:
                    is_valid = False
            elif "f-string" in msg_lower or "string concatenation" in msg_lower:
                # Check for string concatenation patterns
                if "\"" not in line_content and "'" not in line_content:
                    is_valid = False
            elif "magic number" in msg_lower:
                # Check for numeric literals
                if not re.search(r'\b\d+\b', line_content):
                    is_valid = False
            
            if is_valid:
                valid_tasks.append(task)
            else:
                outdated_tasks.append(task)
                
        except Exception as e:
            console.print(f"[yellow]⚠️  Error checking {filepath}: {e}[/]")
            valid_tasks.append(task)  # Assume valid if we can't check
    
    # Show results
    console.print(f"\n[green]✓ Valid tasks: {len(valid_tasks)}[/]")
    if outdated_tasks:
        console.print(f"[yellow]⚠️  Outdated tasks: {len(outdated_tasks)}[/]")
        for task in outdated_tasks[:5]:
            console.print(f"   - {task['file']}:{task['line']} - {task['message'][:50]}")
        if len(outdated_tasks) > 5:
            console.print(f"   ... and {len(outdated_tasks) - 5} more")
    
    # Prune if requested
    if prune and outdated_tasks:
        console.print(f"\n[bold]Pruning {len(outdated_tasks)} outdated tasks...[/]")
        
        # Remove outdated lines from TODO.md
        new_content = todo_content
        for task in outdated_tasks:
            new_content = new_content.replace(task["original_line"] + "\n", "")
        
        # Write back
        todo_path.write_text(new_content)
        console.print(f"[green]✓ Removed {len(outdated_tasks)} outdated tasks from {file}[/]")
    elif prune and not outdated_tasks:
        console.print("\n[green]✓ No outdated tasks to remove[/]")
    else:
        console.print(f"\n[dim]Run with --prune to remove outdated tasks[/]")
    
    console.print(f"\n[bold]{'═' * 60}[/]")
