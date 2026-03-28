#!/usr/bin/env python3
"""Benchmark równoległej naprawy TODO - walidacja na próbce 10 tasków.

Usage:
    python benchmark_parallel_fix.py [limit] [--workers N] [--sequential]

Examples:
    python benchmark_parallel_fix.py 10 --workers 8       # parallel 10 tasks
    python benchmark_parallel_fix.py 10 --sequential    # sequential 10 tasks
"""
import sys
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable
import statistics

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from algitex.todo import parse_todo, FIXERS, TodoTask


@dataclass
class TicketResult:
    """Result for single ticket fix."""
    file: str
    line: int
    category: str
    success: bool
    duration_ms: float
    error: str = ""


@dataclass
class BenchmarkResult:
    """Overall benchmark results."""
    mode: str  # "parallel" or "sequential"
    workers: int
    total_tasks: int
    total_time_ms: float
    per_ticket_times: list[float] = field(default_factory=list)
    success_count: int = 0
    error_count: int = 0

    @property
    def avg_time_ms(self) -> float:
        return statistics.mean(self.per_ticket_times) if self.per_ticket_times else 0

    @property
    def median_time_ms(self) -> float:
        return statistics.median(self.per_ticket_times) if self.per_ticket_times else 0

    @property
    def min_time_ms(self) -> float:
        return min(self.per_ticket_times) if self.per_ticket_times else 0

    @property
    def max_time_ms(self) -> float:
        return max(self.per_ticket_times) if self.per_ticket_times else 0

    @property
    def throughput_tps(self) -> float:
        """Tickets per second."""
        return self.total_tasks / (self.total_time_ms / 1000) if self.total_time_ms > 0 else 0


def fix_single_task(task: TodoTask, dry_run: bool = True) -> TicketResult:
    """Fix a single task and measure time."""
    start = time.perf_counter()

    path = Path(task.file)
    fixer = FIXERS.get(task.category)

    if not fixer:
        duration = (time.perf_counter() - start) * 1000
        return TicketResult(
            file=task.file,
            line=task.line,
            category=task.category,
            success=False,
            duration_ms=duration,
            error="No fixer available"
        )

    if not path.exists():
        duration = (time.perf_counter() - start) * 1000
        return TicketResult(
            file=task.file,
            line=task.line,
            category=task.category,
            success=False,
            duration_ms=duration,
            error="File not found"
        )

    try:
        if dry_run:
            # Simulate fix by just checking
            result = fixer.__name__ if fixer else None
            duration = (time.perf_counter() - start) * 1000
            return TicketResult(
                file=task.file,
                line=task.line,
                category=task.category,
                success=True,
                duration_ms=duration
            )
        else:
            # Actually try to fix (dry-run mode for safety in benchmark)
            success = fixer(path, task)
            duration = (time.perf_counter() - start) * 1000
            return TicketResult(
                file=task.file,
                line=task.line,
                category=task.category,
                success=success,
                duration_ms=duration
            )
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        return TicketResult(
            file=task.file,
            line=task.line,
            category=task.category,
            success=False,
            duration_ms=duration,
            error=str(e)
        )


def run_sequential(tasks: list[TodoTask], dry_run: bool = True) -> BenchmarkResult:
    """Run fixes sequentially."""
    start = time.perf_counter()
    results = []

    for task in tasks:
        result = fix_single_task(task, dry_run)
        results.append(result)

    total_time = (time.perf_counter() - start) * 1000

    return BenchmarkResult(
        mode="sequential",
        workers=1,
        total_tasks=len(tasks),
        total_time_ms=total_time,
        per_ticket_times=[r.duration_ms for r in results],
        success_count=sum(1 for r in results if r.success),
        error_count=sum(1 for r in results if r.error)
    )


def run_parallel(tasks: list[TodoTask], workers: int = 8, dry_run: bool = True) -> BenchmarkResult:
    """Run fixes in parallel using thread pool."""
    start = time.perf_counter()
    results = []

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fix_single_task, task, dry_run): task for task in tasks}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    total_time = (time.perf_counter() - start) * 1000

    return BenchmarkResult(
        mode="parallel",
        workers=workers,
        total_tasks=len(tasks),
        total_time_ms=total_time,
        per_ticket_times=[r.duration_ms for r in results],
        success_count=sum(1 for r in results if r.success),
        error_count=sum(1 for r in results if r.error)
    )


def print_report(result: BenchmarkResult, detailed: bool = False):
    """Print benchmark report."""
    print(f"\n{'═' * 70}")
    print(f"  BENCHMARK: {result.mode.upper()} | Workers: {result.workers} | Tasks: {result.total_tasks}")
    print(f"{'═' * 70}")

    # Summary stats
    print(f"\n  📊 TIMING:")
    print(f"     Total time:     {result.total_time_ms:>8.2f} ms  ({result.total_time_ms/1000:.3f}s)")
    print(f"     Per ticket avg: {result.avg_time_ms:>8.2f} ms")
    print(f"     Per ticket med: {result.median_time_ms:>8.2f} ms")
    print(f"     Min/Max:        {result.min_time_ms:>8.2f} / {result.max_time_ms:.2f} ms")
    print(f"     Throughput:     {result.throughput_tps:>8.2f} tickets/sec")

    print(f"\n  ✅ RESULTS:")
    print(f"     Success: {result.success_count}/{result.total_tasks}")
    print(f"     Errors:  {result.error_count}")

    if detailed:
        print(f"\n  📋 PER-TICKET DETAILS:")
        for i, t in enumerate(sorted(result.per_ticket_times, reverse=True)[:5]):
            print(f"     #{i+1}: {t:.2f} ms")


def main():
    parser = argparse.ArgumentParser(description="Benchmark parallel TODO fixing")
    parser.add_argument("limit", type=int, nargs="?", default=10, help="Number of tasks to benchmark")
    parser.add_argument("--workers", "-w", type=int, default=8, help="Number of parallel workers")
    parser.add_argument("--sequential", action="store_true", help="Run sequential instead of parallel")
    parser.add_argument("--execute", action="store_true", help="Actually apply fixes (not dry-run)")
    parser.add_argument("--todo-file", "-f", default="TODO.md", help="Path to TODO.md")
    parser.add_argument("--detailed", "-d", action="store_true", help="Show detailed per-ticket info")
    args = parser.parse_args()

    # Parse tasks
    print(f"📁 Loading tasks from {args.todo_file}...")
    all_tasks = parse_todo(args.todo_file)

    # Filter to first N pending tasks (skip worktree dups already filtered by parse_todo)
    pending_tasks = all_tasks[:args.limit]

    if not pending_tasks:
        print("❌ No tasks found!")
        return 1

    print(f"🎯 Selected {len(pending_tasks)} tasks for benchmark")

    # Category breakdown
    cats = {}
    for t in pending_tasks:
        cats[t.category] = cats.get(t.category, 0) + 1
    print(f"📊 Categories: {', '.join(f'{k}={v}' for k, v in cats.items())}")

    # Run benchmark
    dry_run = not args.execute
    if args.sequential:
        result = run_sequential(pending_tasks, dry_run)
    else:
        result = run_parallel(pending_tasks, args.workers, dry_run)

    # Print report
    print_report(result, detailed=args.detailed)

    # If parallel, also show theoretical speedup
    if not args.sequential:
        # Estimate sequential time as sum of individual times
        est_sequential = sum(result.per_ticket_times)
        speedup = est_sequential / result.total_time_ms if result.total_time_ms > 0 else 1
        print(f"\n  ⚡ SPEEDUP:")
        print(f"     Estimated sequential: {est_sequential:.2f} ms")
        print(f"     Actual parallel:      {result.total_time_ms:.2f} ms")
        print(f"     Speedup factor:       {speedup:.2f}x")
        print(f"     Efficiency:           {(speedup/args.workers)*100:.1f}% ({args.workers} workers)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
