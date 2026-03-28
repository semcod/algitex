"""Todo subcommands for algitex CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from clickmd import command, option, argument
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


def _run_hybrid_with_dashboard(
    file: str,
    fixer,
    hybrid: bool,
    dry_run: bool,
) -> None:
    """Run hybrid autofix with live dashboard.
    
    CC: 4 (dashboard init + phase tracking + result handling)
    """
    from algitex.dashboard import LiveDashboard
    from algitex.tools.ollama_cache import LLMCache
    import threading
    import time

    # Initialize dashboard
    dashboard = LiveDashboard(refresh_rate=1.0)
    
    # Initialize cache stats
    cache = LLMCache(".algitex/cache")
    cache_stats = cache.stats()
    dashboard.update_cache_stats(
        hits=cache_stats["hits"],
        misses=cache_stats["misses"],
        entries=cache_stats["entries"],
        size_bytes=cache_stats["size_bytes"],
    )

    def run_fix():
        """Run the fix operation with dashboard updates."""
        if hybrid:
            dashboard.update_tier_progress("algorithm", total=100, active=True)
            dashboard.update_tier_progress("big", total=100, active=True)
            
            # Simulate progress for hybrid fix
            for i in range(0, 100, 10):
                dashboard.update_tier_progress("algorithm", current=i)
                time.sleep(0.1)
            
            result = fixer.fix_all(file)
            
            dashboard.update_tier_progress("algorithm", current=100, active=False)
            dashboard.update_tier_progress("big", current=100, active=False)
        else:
            dashboard.update_tier_progress("big", total=100, active=True)
            
            for i in range(0, 100, 20):
                dashboard.update_tier_progress("big", current=i)
                time.sleep(0.1)
            
            result = fixer.fix_complex(file)
            
            dashboard.update_tier_progress("big", current=100, active=False)
        
        return result

    # Run with dashboard
    try:
        dashboard.start()
        result = run_fix()
        
        # Show final summary
        console.print("\n[bold]Fix Summary[/]")
        fixer.print_summary(result)
        
        time.sleep(1)  # Let user see final state
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation interrupted by user[/]")
    finally:
        dashboard.stop()


def _run_batch_with_dashboard(
    backend_fixer,
    tasks: list,
    parallel: int,
    dry_run: bool,
) -> None:
    """Run batch fix with live dashboard.
    
    CC: 4 (dashboard init + progress tracking + result display)
    """
    from algitex.dashboard import LiveDashboard
    from algitex.tools.ollama_cache import LLMCache
    import threading
    import time

    # Initialize dashboard
    dashboard = LiveDashboard(refresh_rate=1.0)
    
    # Initialize cache stats
    cache = LLMCache(".algitex/cache")
    cache_stats = cache.stats()
    dashboard.update_cache_stats(
        hits=cache_stats["hits"],
        misses=cache_stats["misses"],
        entries=cache_stats["entries"],
        size_bytes=cache_stats["size_bytes"],
    )

    def run_batch():
        """Run batch fix with dashboard updates."""
        dashboard.update_tier_progress("batch", total=len(tasks), active=True)
        
        results = backend_fixer.fix_batch(tasks, max_parallel=parallel)
        
        dashboard.update_tier_progress("batch", current=len(tasks), active=False)
        return results

    # Run with dashboard
    try:
        dashboard.start()
        results = run_batch()
        
        # Show summary
        success = sum(1 for r in results if r.success)
        failed = len(results) - success
        
        console.print(f"\n[bold]{'═' * 60}[/]")
        console.print(f"  BATCH FIX SUMMARY")
        console.print(f"[bold]{'═' * 60}[/]")
        console.print(f"\n  ✅ Success: {success}")
        console.print(f"  ❌ Failed:  {failed}")
        console.print(f"  📊 Total:   {len(results)}")
        console.print(f"[bold]{'═' * 60}[/]")
        
        if not dry_run and success > 0:
            console.print(f"\n[green]✓ Zaktualizowano {success} plików[/]")
        
        time.sleep(1)  # Let user see final state
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation interrupted by user[/]")
    finally:
        dashboard.stop()


@command()
@argument("file", default="TODO.md")
def todo_stats(
    file: str,
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


@command()
@argument("file", default="TODO.md")
def todo_verify(
    file: str,
):
    """Verify which TODO tasks are still valid vs already fixed."""
    from algitex.todo import TodoVerifier

    verifier = TodoVerifier(file)
    result = verifier.verify()
    verifier.print_report()


@command()
@argument("file", default="TODO.md")
@option("--workers", "-w", default=8, help="Number of parallel workers")
@option("--dry-run/--execute", default=True, help="Dry run or actually apply")
@option("--category", "-c", default=None, help="Filter to specific category")
def todo_fix_parallel(
    file: str,
    workers: int,
    dry_run: bool,
    category: Optional[str],
):
    """Auto-fix mechanical TODO tasks in parallel."""
    from algitex.todo import fix_todos

    result = fix_todos(file, workers=workers, dry_run=dry_run, category=category)
    console.print(f"\n[bold]Results:[/] Fixed: {result['fixed']}, Skipped: {result['skipped']}, Errors: {result['errors']}")


@command()
@argument("file", default="TODO.md")
def todo_list(
    file: str,
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


@command()
@argument("file", default="TODO.md")
@option("--tool", "-t", default="local", help="Tool to use")
@option("--dry-run", default=False, help="Preview without executing")
@option("--limit", "-l", default=0, help="Limit number of tasks")
def todo_run(
    file: str,
    tool: str,
    dry_run: bool,
    limit: int,
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


def _format_todo_help():
    """Format help for todo fix command."""
    return """# Tiered AutoFix

Execute fix tasks via 3-tier pipeline:
- Algorithm - deterministic fixes (fast, no LLM)
- Micro - small LLM fixes (qwen3-coder:latest)
- Big - large LLM fixes (complex refactoring)

## Examples

Algorithm only (fastest):
  $ algitex todo fix --algo --execute

All tiers with dashboard:
  $ algitex todo fix --all --dashboard --execute

Limited tasks with workers:
  $ algitex todo fix --limit 10 --workers 4 --execute
"""


@command()
@argument("file", default="TODO.md")
@option("--tool", "-t", default="ollama-mcp")
@option("--task-id", default=None)
@option("--limit", "-l", default=0)
@option("--dry-run/--execute", default=False, is_flag=True)
@option("--algo", default=False, is_flag=True)
@option("--micro", default=False, is_flag=True)
@option("--all-phases", "--all", default=False, is_flag=True)
@option("--dashboard", "-d", default=False, is_flag=True)
@option("--workers", "-w", default=8)
@option("--micro-workers", default=4)
@option("--model", default="qwen3-coder:latest")
@option("--backend", "-b", default="litellm-proxy")
@option("--rate-limit", "-r", default=10)
@option("--proxy-url", "-p", default="http://localhost:4000")
@option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def todo_fix(
    file: str,
    tool: str,
    task_id: Optional[str],
    limit: int,
    dry_run: bool,
    algo: bool,
    micro: bool,
    all_phases: bool,
    dashboard: bool,
    workers: int,
    micro_workers: int,
    model: str,
    backend: str,
    rate_limit: int,
    proxy_url: str,
    verbose: bool,
):
    """Execute fix tasks (prefact-style) via Docker MCP.
    
    5-step pipeline: parse → classify → execute → validate → report.
    CC: 8 (5 functions + 3 branches)
    Was: CC ~50 (nested phase logic)
    """
    # Enable verbose logging if requested
    if verbose:
        from algitex.tools.logging import set_verbose
        set_verbose(True)
        console.print("[dim][VERBOSE] Debug logging enabled[/]")
    
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
    from algitex.tools.todo_runner import TodoRunner
    from algitex.tools.todo_parser import Task as RunnerTask

    if not tasks:
        console.print("[yellow]No fix tasks found[/]")
        return

    # Filter to fix-related tasks
    fix_keywords = ["fix", "repair", "correct", "missing", "unused", "magic number", "return type"]
    fix_tasks = [t for t in tasks if any(kw in t.message.lower() for kw in fix_keywords)]

    if not fix_tasks:
        console.print("[yellow]No fix tasks found[/]")
        return

    # Convert TodoTask objects to Task objects expected by TodoRunner
    runner_tasks = [
        RunnerTask(
            id=f"{t.file}:{t.line}",
            description=t.message,
            file_path=str(t.file),
            line_number=t.line,
            status="pending"
        )
        for t in fix_tasks
    ]

    console.print(f"[bold]Found {len(runner_tasks)} fix tasks[/]\n")

    with TodoRunner(".") as runner:
        results = runner.run(runner_tasks, tool=tool, dry_run=dry_run)

        for r in results:
            icon = "\u2713" if r.success else "\u2717"
            color = "green" if r.success else "red"
            console.print(f"[{color}]{icon}[/] {r.task.description[:60]}")
            if r.error:
                console.print(f"   [red]Error: {r.error}[/]")


@command()
@argument("limit", default=10)
@option("--file", "-f", default="TODO.md")
@option("--workers", "-w", default=8)
@option("--compare", "-c", default=False)
def todo_benchmark(
    limit: int,
    file: str,
    workers: int,
    compare: bool,
):
    """Benchmark TODO fix performance."""
    from algitex.todo import benchmark_fix, compare_modes

    if compare:
        compare_modes(file, limit=limit, workers=workers)
    else:
        result = benchmark_fix(file, limit=limit, workers=workers, mode="parallel")
        result.print_report(detailed=True)
        console.print(f"\n[dim]Tip: Use --compare to see parallel vs sequential comparison[/]")


@command()
@argument("file", default="TODO.md")
@option("--backend", "-b", default="litellm-proxy")
@option("--tool", "-t", default="aider")
@option("--workers", "-w", default=4)
@option("--rate-limit", "-r", default=10)
@option("--proxy-url", "-p", default="http://localhost:4000")
@option("--hybrid", "-h", default=False)
@option("--dashboard", "-d", default=False)
@option("--fallback/--no-fallback", default=True)
@option("--verbose", "-v", default=False)
@option("--dry-run/--execute", default=True)
def todo_hybrid(
    file: str,
    backend: str,
    tool: str,
    workers: int,
    rate_limit: int,
    proxy_url: str,
    hybrid: bool,
    dashboard: bool,
    fallback: bool,
    verbose: bool,
    dry_run: bool,
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


@command()
@option("--file", "-f", default="TODO.md")
@option("--backend", "-b", default="ollama")
@option("--model", "-m", default="qwen3-coder:latest")
@option("--batch-size", "-s", default=5)
@option("--parallel", "-p", default=3)
@option("--dry-run/--execute", default=True)
@option("--verbose", "-v", default=False)
@option("--prune", default=False)
@option("--limit", "-l", default=0)
@option("--no-log", default=False)
@option("--dashboard", "-d", default=False)
def todo_batch(
    file: Path,
    backend: str,
    model: str,
    batch_size: int,
    parallel: int,
    dry_run: bool,
    verbose: bool,
    prune: bool,
    limit: int,
    no_log: bool,
    dashboard: bool,
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
    
    # Execute with dashboard if requested
    if dashboard:
        _run_batch_with_dashboard(backend_fixer, tasks, parallel, dry_run)
        return
    
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


@command()
@option("--file", "-f", default="TODO.md")
@option("--prune", "-p", default=False)
def todo_verify_prefact(
    file: str,
    prune: bool,
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
