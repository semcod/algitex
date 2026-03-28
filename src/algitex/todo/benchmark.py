"""Benchmark utilities for TODO fixing performance measurement.

Usage:
    from algitex.todo.benchmark import benchmark_fix

    result = benchmark_fix("TODO.md", limit=100, workers=8)
    print(f"Throughput: {result.throughput_tps:.2f} tickets/sec")
"""
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from algitex.todo.fixer import parse_todo, FIXERS, TodoTask


@dataclass
class BenchmarkResult:
    """Benchmark results for fix operations."""
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
    def stdev_time_ms(self) -> float:
        return statistics.stdev(self.per_ticket_times) if len(self.per_ticket_times) > 1 else 0

    @property
    def throughput_tps(self) -> float:
        """Tickets per second."""
        return self.total_tasks / (self.total_time_ms / 1000) if self.total_time_ms > 0 else 0

    def print_report(self, detailed: bool = False) -> None:
        """Print formatted benchmark report."""
        print(f"\n{'═' * 70}")
        print(f"  BENCHMARK: {self.mode.upper()} | Workers: {self.workers} | Tasks: {self.total_tasks}")
        print(f"{'═' * 70}")

        print(f"\n  📊 TIMING:")
        print(f"     Total time:     {self.total_time_ms:>10.2f} ms  ({self.total_time_ms/1000:.3f}s)")
        print(f"     Per ticket avg: {self.avg_time_ms:>10.2f} ms")
        print(f"     Per ticket med: {self.median_time_ms:>10.2f} ms")
        print(f"     Std dev:        {self.stdev_time_ms:>10.2f} ms")
        print(f"     Min/Max:        {self.min_time_ms:>10.2f} / {self.max_time_ms:.2f} ms")
        print(f"     Throughput:     {self.throughput_tps:>10.2f} tickets/sec")

        print(f"\n  ✅ RESULTS:")
        print(f"     Success: {self.success_count}/{self.total_tasks}")
        print(f"     Errors:  {self.error_count}")

        if detailed and self.per_ticket_times:
            print(f"\n  📋 PER-TICKET DETAILS (top 5 slowest):")
            sorted_times = sorted(self.per_ticket_times, reverse=True)
            for i, t in enumerate(sorted_times[:5]):
                print(f"     #{i+1}: {t:>8.2f} ms")


def _benchmark_single(task: TodoTask, dry_run: bool = True) -> tuple[bool, float, str]:
    """Benchmark single task fix. Returns (success, duration_ms, error)."""
    start = time.perf_counter()

    path = Path(task.file)
    fixer = FIXERS.get(task.category)

    if not fixer:
        duration = (time.perf_counter() - start) * 1000
        return False, duration, "No fixer available"

    if not path.exists():
        duration = (time.perf_counter() - start) * 1000
        return False, duration, "File not found"

    try:
        if dry_run:
            # Simulate: just check if fixer exists
            duration = (time.perf_counter() - start) * 1000
            return True, duration, ""
        else:
            success = fixer(path, task)
            duration = (time.perf_counter() - start) * 1000
            return success, duration, "" if success else "Fix failed"
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        return False, duration, str(e)


def benchmark_sequential(
    tasks: list[TodoTask],
    dry_run: bool = True
) -> BenchmarkResult:
    """Run sequential benchmark."""
    start = time.perf_counter()
    times = []
    success = 0
    errors = 0

    for task in tasks:
        ok, duration, error = _benchmark_single(task, dry_run)
        times.append(duration)
        if ok:
            success += 1
        if error:
            errors += 1

    total_time = (time.perf_counter() - start) * 1000

    return BenchmarkResult(
        mode="sequential",
        workers=1,
        total_tasks=len(tasks),
        total_time_ms=total_time,
        per_ticket_times=times,
        success_count=success,
        error_count=errors
    )


def benchmark_parallel(
    tasks: list[TodoTask],
    workers: int = 8,
    dry_run: bool = True
) -> BenchmarkResult:
    """Run parallel benchmark."""
    start = time.perf_counter()
    times = []
    success = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_benchmark_single, task, dry_run): task for task in tasks}

        for future in as_completed(futures):
            ok, duration, error = future.result()
            times.append(duration)
            if ok:
                success += 1
            if error:
                errors += 1

    total_time = (time.perf_counter() - start) * 1000

    return BenchmarkResult(
        mode="parallel",
        workers=workers,
        total_tasks=len(tasks),
        total_time_ms=total_time,
        per_ticket_times=times,
        success_count=success,
        error_count=errors
    )


def benchmark_fix(
    todo_path: str | Path = "TODO.md",
    limit: int = 10,
    workers: int = 8,
    dry_run: bool = True,
    mode: str = "parallel"
) -> BenchmarkResult:
    """Run benchmark on TODO tasks.

    Args:
        todo_path: Path to TODO.md file
        limit: Number of tasks to benchmark
        workers: Number of parallel workers (for parallel mode)
        dry_run: If True, simulate fixes without applying
        mode: "parallel" or "sequential"

    Returns:
        BenchmarkResult with timing statistics
    """
    tasks = parse_todo(todo_path)[:limit]

    if mode == "parallel":
        return benchmark_parallel(tasks, workers, dry_run)
    else:
        return benchmark_sequential(tasks, dry_run)


def compare_modes(
    todo_path: str | Path = "TODO.md",
    limit: int = 10,
    workers: int = 8,
    dry_run: bool = True
) -> dict:
    """Compare parallel vs sequential execution.

    Returns:
        Dict with both results and speedup analysis
    """
    tasks = parse_todo(todo_path)[:limit]

    print(f"🔬 COMPARISON MODE: {limit} tasks, {workers} workers")
    print(f"{'─' * 70}")

    # Sequential
    seq_result = benchmark_sequential(tasks, dry_run)
    seq_result.print_report(detailed=False)

    # Parallel
    par_result = benchmark_parallel(tasks, workers, dry_run)
    par_result.print_report(detailed=False)

    # Analysis
    speedup = seq_result.total_time_ms / par_result.total_time_ms if par_result.total_time_ms > 0 else 1
    efficiency = (speedup / workers) * 100

    print(f"\n{'═' * 70}")
    print(f"  ⚡ SPEEDUP ANALYSIS")
    print(f"{'═' * 70}")
    print(f"     Sequential time:  {seq_result.total_time_ms:>10.2f} ms")
    print(f"     Parallel time:    {par_result.total_time_ms:>10.2f} ms")
    print(f"     Speedup factor:   {speedup:>10.2f}x")
    print(f"     Efficiency:       {efficiency:>9.1f}% ({workers} workers)")
    print(f"     Winner:           {'PARALLEL' if speedup > 1 else 'SEQUENTIAL'}")

    return {
        "sequential": seq_result,
        "parallel": par_result,
        "speedup": speedup,
        "efficiency": efficiency,
        "winner": "parallel" if speedup > 1 else "sequential"
    }
