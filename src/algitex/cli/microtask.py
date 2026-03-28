"""CLI commands for the MicroTask pipeline."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from algitex.microtask import MicroTask, TaskType, group_tasks_by_file
from algitex.microtask.classifier import classify_todo_file
from algitex.microtask.executor import MicroTaskExecutor
from algitex.microtask.slicer import ContextSlicer


console = Console()
microtask_app = typer.Typer(help="Atomic MicroTask pipeline for small LLMs.")


@microtask_app.command("classify")
def microtask_classify(
    todo_path: str = typer.Argument("TODO.md", help="Path to a prefact-style TODO file."),
) -> None:
    """Classify TODO items into atomic MicroTasks."""
    tasks = classify_todo_file(todo_path)
    if not tasks:
        console.print("[yellow]No open microtasks found.[/yellow]")
        raise typer.Exit()

    _print_summary(tasks, title="MicroTask classification")
    _print_task_table(tasks)


@microtask_app.command("plan")
def microtask_plan(
    todo_path: str = typer.Argument("TODO.md", help="Path to a prefact-style TODO file."),
) -> None:
    """Show execution plan, tiers, and model hints."""
    tasks = classify_todo_file(todo_path)
    if not tasks:
        console.print("[yellow]No open microtasks found.[/yellow]")
        raise typer.Exit()

    slicer = ContextSlicer(Path(todo_path).resolve().parent)
    for task in tasks:
        slicer.slice(task)

    _print_summary(tasks, title="Execution plan")
    _print_plan_table(tasks)
    _print_file_batches(tasks)


@microtask_app.command("run")
def microtask_run(
    todo_path: str = typer.Argument("TODO.md", help="Path to a prefact-style TODO file."),
    algo_only: bool = typer.Option(False, "--algo-only", help="Run only deterministic tasks."),
    tier: int | None = typer.Option(None, "--tier", min=0, max=3, help="Run only tasks from a single tier."),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Preview changes without writing files."),
    workers: int = typer.Option(8, "--workers", min=1, help="Parallel workers for deterministic tasks."),
    llm_workers: int = typer.Option(4, "--llm-workers", min=1, help="Parallel workers for small LLM tasks."),
    rate_limit: float = typer.Option(10.0, "--rate-limit", min=0.1, help="LLM requests per second."),
) -> None:
    """Execute the three-phase microtask pipeline."""
    tasks = classify_todo_file(todo_path)
    tasks = _filter_tasks(tasks, algo_only=algo_only, tier=tier)

    if not tasks:
        console.print("[yellow]No tasks matched the selected filters.[/yellow]")
        raise typer.Exit()

    executor = MicroTaskExecutor(
        project_path=Path(todo_path).resolve().parent,
        algo_workers=workers,
        llm_workers=llm_workers,
        rate_limit_rps=rate_limit,
    )

    try:
        results = executor.execute(tasks, dry_run=dry_run)
    finally:
        executor.close()

    _print_phase_results(results, dry_run=dry_run)


def _filter_tasks(tasks: list[MicroTask], *, algo_only: bool, tier: int | None) -> list[MicroTask]:
    if algo_only:
        return [task for task in tasks if task.tier == 0]
    if tier is not None:
        return [task for task in tasks if task.tier == tier]
    return tasks


def _print_summary(tasks: list[MicroTask], *, title: str) -> None:
    counts = Counter(task.tier for task in tasks)
    total_tokens = sum(task.context_tokens for task in tasks)
    table = Table(title=title, show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Total", str(len(tasks)))
    table.add_row("Tier 0", str(counts.get(0, 0)))
    table.add_row("Tier 1", str(counts.get(1, 0)))
    table.add_row("Tier 2", str(counts.get(2, 0)))
    table.add_row("Tier 3", str(counts.get(3, 0)))
    table.add_row("Estimated context tokens", str(total_tokens))
    console.print(table)


def _print_task_table(tasks: list[MicroTask]) -> None:
    table = Table(title="MicroTasks")
    table.add_column("ID", style="bold")
    table.add_column("Tier")
    table.add_column("Type")
    table.add_column("Model")
    table.add_column("File")
    table.add_column("Lines")
    table.add_column("Scope")
    for task in tasks:
        scope = task.function_name or task.class_name or "module"
        table.add_row(
            task.id,
            str(task.tier),
            task.type.value,
            task.type.model_hint,
            _shorten_path(task.file),
            f"{task.line_start}-{task.line_end}",
            scope,
        )
    console.print(table)


def _print_plan_table(tasks: list[MicroTask]) -> None:
    table = Table(title="Model plan")
    table.add_column("Type", style="bold")
    table.add_column("Tier")
    table.add_column("Model")
    table.add_column("Count", justify="right")
    counts = Counter(task.type for task in tasks)
    for task_type, count in sorted(counts.items(), key=lambda item: (item[0].tier, item[0].value)):
        table.add_row(task_type.value, str(task_type.tier), task_type.model_hint, str(count))
    console.print(table)


def _print_file_batches(tasks: list[MicroTask]) -> None:
    batches = group_tasks_by_file(tasks)
    table = Table(title="File batches")
    table.add_column("File")
    table.add_column("Total", justify="right")
    table.add_column("Algorithmic", justify="right")
    table.add_column("LLM", justify="right")
    for batch in batches:
        stats = batch.stats()
        table.add_row(
            _shorten_path(str(stats["file"])),
            str(stats["total"]),
            str(stats["algorithmic"]),
            str(stats["llm"]),
        )
    console.print(table)


def _print_phase_results(results: list, *, dry_run: bool) -> None:
    table = Table(title="MicroTask execution" if not dry_run else "MicroTask plan")
    table.add_column("Phase", style="bold")
    table.add_column("Total", justify="right")
    table.add_column("Fixed", justify="right")
    table.add_column("Skipped", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Duration ms", justify="right")
    for result in results:
        table.add_row(
            result.name,
            str(result.total),
            str(result.fixed),
            str(result.skipped),
            str(result.errors),
            f"{result.duration_ms:.1f}",
        )
    console.print(table)


def _shorten_path(path: str, max_len: int = 72) -> str:
    if len(path) <= max_len:
        return path
    return f"…{path[-(max_len - 1):]}"


__all__ = ["microtask_app", "microtask_classify", "microtask_plan", "microtask_run"]
