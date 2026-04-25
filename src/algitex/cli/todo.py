from rich.table import Table
from rich.console import Console

console = Console()

def _render_todo_stats(file: str, tasks) -> None:
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
    console.print(f"\n[bold]Total:[/] {summary.total} | Algorithm: {summary.algorithmic} | Micro: {summary.micro} | Big: {summary.big}")

def _run_algo_phase(file: str, tasks: list, workers: int, dry_run: bool) -> dict:
    from algitex.todo import parallel_fix_and_update
    console.print(f"\n[green]Phase 1: Algorithm[/] — {len(tasks)} tasks")
    return parallel_fix_and_update(file, workers=workers, dry_run=dry_run, tasks=tasks)

def _run_micro_phase(file: str, tasks: list, model: str, micro_workers: int, dry_run: bool) -> dict:
    from algitex.todo import MicroFixer, mark_tasks_completed
    console.print(f"\n[cyan]Phase 2: Small LLM[/] — {len(tasks)} tasks")
    micro_fixer = MicroFixer(ollama_url="http://localhost:11434", model=model, workers=micro_workers, dry_run=dry_run)
    micro_results = micro_fixer.fix_tasks_detailed(tasks)
    result = {"fixed": sum(1 for item in micro_results if item.success), "skipped": sum(1 for item in micro_results if not item.success and not item.error), "errors": sum(1 for item in micro_results if item.error)}
    if not dry_run and result.get("fixed", 0) > 0:
        completed_ids = {item.task_id for item in micro_results if item.success}
        completed_tasks = [t for t in tasks if f"{t.file}:{t.line}" in completed_ids]
        if completed_tasks:
            mark_tasks_completed(file, completed_tasks)
    return result

def _run_big_phase(file: str, tasks: list, backend: str, proxy_url: str, workers: int, rate_limit: int, dry_run: bool) -> dict:
    from algitex.todo import BIG_CATEGORIES, HybridAutofix, mark_tasks_completed
    console.print(f"\n[magenta]Phase 3: Big LLM[/] — {len(tasks)} tasks")
    fixer = HybridAutofix(backend=backend, tool="ollama-mcp", proxy_url=proxy_url, workers=workers, rate_limit=rate_limit, dry_run=dry_run)
    result = fixer.fix_complex(file, include_categories=set(BIG_CATEGORIES), tasks=tasks)
    if not dry_run and result.get("fixed", 0) == len(tasks) and tasks:
        mark_tasks_completed(file, tasks)
    return result

def _tf_execute_phased(file: str, classified: dict[str, list], algo: bool, micro: bool, all_phases: bool, workers: int, micro_workers: int, model: str, backend: str, rate_limit: int, proxy_url: str, dry_run: bool) -> list[tuple[str, dict]]:
    results: list[tuple[str, dict]] = []
    if all_phases:
        algo = True
        micro = True
    if algo and classified.get("algorithm"):
        results.append(("Algorithm", _run_algo_phase(file, classified["algorithm"], workers, dry_run)))
    if micro and classified.get("micro"):
        results.append(("Small LLM", _run_micro_phase(file, classified["micro"], model, micro_workers, dry_run)))
    if all_phases and classified.get("big"):
        results.append(("Big LLM", _run_big_phase(file, classified["big"], backend, proxy_url, workers, rate_limit, dry_run)))
    return results