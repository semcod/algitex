"""Hybrid Autofix — combines fast parallel mechanical fixes with LLM-based fixes.

This module provides the missing piece: fast + parallel + LLM with rate limiting.

Usage:
    from algitex.todo.hybrid import HybridAutofix

    fixer = HybridAutofix(
        backend="litellm-proxy",
        proxy_url="http://localhost:4000",
        workers=4,
        rate_limit=10,  # 10 LLM calls per second
        retry_attempts=3
    )

    # Phase 1: Fast parallel mechanical fixes
    mechanical_results = fixer.fix_mechanical("TODO.md")

    # Phase 2: Parallel LLM fixes with rate limiting
    llm_results = fixer.fix_complex("TODO.md")
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from collections import deque
import threading

from algitex.todo.fixer import parse_todo, FIXERS, TodoTask, fix_file, FixResult
from algitex.todo.verifier import TodoVerifier


@dataclass
class HybridResult:
    """Result of hybrid fix operation."""
    mechanical: dict = field(default_factory=dict)
    llm: dict = field(default_factory=dict)
    total_time_sec: float = 0.0
    cost_estimate: float = 0.0


class RateLimiter:
    """Token bucket rate limiter for LLM calls."""

    def __init__(self, rate: float = 10.0, burst: int = 5):
        """Initialize rate limiter.

        Args:
            rate: Maximum sustained rate (calls per second)
            burst: Maximum burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> float:
        """Acquire a token, return wait time if any."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return 0.0
            else:
                wait_time = (1.0 - self.tokens) / self.rate
                self.tokens = 0.0
                return wait_time


@dataclass
class LLMTask:
    """Task for LLM-based fixing."""
    task: TodoTask
    file_content: str = ""
    context_lines: int = 5


class HybridAutofix:
    """Hybrid autofix: parallel mechanical + rate-limited parallel LLM.

    Combines the speed of regex-based fixes with intelligence of LLM fixes,
    all while respecting rate limits and tracking costs.

    Example:
        fixer = HybridAutofix(
            backend="litellm-proxy",
            proxy_url="http://localhost:4000",
            workers=4,
            rate_limit=10
        )

        # Run both phases
        result = fixer.fix_all("TODO.md")
        print(f"Mechanical: {result.mechanical}")
        print(f"LLM: {result.llm}")
        print(f"Total time: {result.total_time_sec:.2f}s")
    """

    def __init__(
        self,
        backend: str = "litellm-proxy",  # or "ollama", "aider"
        tool: str = "aider",  # Tool selection: aider, ollama, direct
        proxy_url: str = "http://localhost:4000",
        workers: int = 4,
        rate_limit: float = 10.0,
        retry_attempts: int = 3,
        timeout: float = 30.0,
        dry_run: bool = True
    ):
        self.backend = backend
        self.tool = tool
        self.proxy_url = proxy_url
        self.workers = workers
        self.rate_limiter = RateLimiter(rate=rate_limit)
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self.dry_run = dry_run

        # Statistics
        self.llm_calls = 0
        self.llm_errors = 0
        self.total_cost = 0.0

    def fix_mechanical(self, todo_path: str | Path) -> dict:
        """Phase 1: Fast parallel mechanical fixes.

        Uses ThreadPoolExecutor with FIXERS (no LLM calls).
        Throughput: ~1500 tickets/sec

        Returns:
            Dict with fixed, skipped, errors counts
        """
        from algitex.todo import fix_todos

        print(f"🔧 Phase 1: Mechanical fixes (workers={self.workers})")
        start = time.perf_counter()

        result = fix_todos(
            str(todo_path),
            workers=self.workers,
            dry_run=self.dry_run
        )

        elapsed = time.perf_counter() - start
        print(f"   ✓ Fixed: {result['fixed']}, Skipped: {result['skipped']}, Errors: {result['errors']}")
        print(f"   ⏱️  Time: {elapsed:.3f}s ({result['fixed'] / elapsed:.0f} tickets/sec)")

        return result

    def fix_complex(self, todo_path: str | Path) -> dict:
        """Phase 2: Rate-limited parallel LLM fixes.

        Uses ThreadPoolExecutor with rate limiting for LLM calls.
        Throughput: ~rate_limit tickets/sec (e.g., 10/sec)

        Returns:
            Dict with fixed, skipped, errors counts
        """
        print(f"\n🤖 Phase 2: LLM fixes (backend={self.backend}, tool={self.tool}, rate={self.rate_limiter.rate}/sec)")
        start = time.perf_counter()

        # Parse and categorize tasks
        all_tasks = parse_todo(todo_path)

        # Filter to LLM-handled categories (not in FIXERS)
        llm_tasks = [t for t in all_tasks if t.category not in FIXERS]

        if not llm_tasks:
            print("   ℹ️  No complex tasks requiring LLM")
            return {"fixed": 0, "skipped": 0, "errors": 0}

        print(f"   📋 {len(llm_tasks)} tasks for LLM processing")

        # Group by file
        by_file: dict[str, list[TodoTask]] = {}
        for task in llm_tasks:
            by_file.setdefault(task.file, []).append(task)

        # Process with rate limiting
        results = self._process_llm_parallel(by_file)

        elapsed = time.perf_counter() - start
        print(f"   ✓ Fixed: {results['fixed']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
        print(f"   ⏱️  Time: {elapsed:.3f}s ({results['fixed'] / elapsed:.1f} tickets/sec)")
        print(f"   💰 Est. cost: ${self.total_cost:.4f}")

        return results

    def _process_llm_parallel(self, by_file: dict) -> dict:
        """Process LLM tasks with rate limiting."""
        total_fixed = 0
        total_skipped = 0
        total_errors = 0

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {}

            for file_path, tasks in by_file.items():
                # Rate limit: acquire token before submitting
                wait = self.rate_limiter.acquire()
                if wait > 0:
                    time.sleep(wait)

                future = pool.submit(self._fix_file_llm, file_path, tasks)
                futures[future] = file_path

            for future in as_completed(futures):
                try:
                    result = future.result()
                    total_fixed += result.get("fixed", 0)
                    total_skipped += result.get("skipped", 0)
                    total_errors += result.get("errors", 0)
                except Exception as e:
                    print(f"   ✗ Error: {e}")
                    total_errors += 1

        return {
            "fixed": total_fixed,
            "skipped": total_skipped,
            "errors": total_errors
        }

    def _fix_file_llm(self, file_path: str, tasks: list[TodoTask]) -> dict:
        """Fix single file via LLM backend with retries."""
        path = Path(file_path)
        if not path.exists():
            return {"fixed": 0, "skipped": len(tasks), "errors": 0}

        fixed = 0
        skipped = 0
        errors = 0

        for task in sorted(tasks, key=lambda t: t.line, reverse=True):
            for attempt in range(self.retry_attempts):
                try:
                    if self.dry_run:
                        # Simulate LLM fix
                        self.llm_calls += 1
                        self.total_cost += 0.002  # $0.002 per call estimate
                        fixed += 1
                    else:
                        # Actual LLM call via backend
                        success = self._call_llm_backend(task, path)
                        self.llm_calls += 1
                        if success:
                            fixed += 1
                            self.total_cost += 0.002
                        else:
                            skipped += 1
                    break  # Success, exit retry loop

                except Exception as e:
                    if attempt == self.retry_attempts - 1:
                        print(f"   ✗ Failed after {self.retry_attempts} attempts: {task.file}:{task.line}")
                        errors += 1
                        self.llm_errors += 1
                    else:
                        # Exponential backoff: 1s, 2s, 4s
                        time.sleep(2 ** attempt)

        return {"fixed": fixed, "skipped": skipped, "errors": errors}

    def _call_llm_backend(self, task: TodoTask, path: Path) -> bool:
        """Call LLM backend to fix a task.

        Integrates with:
        - litellm-proxy: via ProxyBackend (HTTP API calls)
        - ollama: via OllamaBackend (local LLM)
        - aider: via AiderBackend (aider CLI)
        """
        try:
            from algitex.tools.autofix.fallback_backend import FallbackBackend
            from algitex.tools.autofix.base import Task

            # Convert TodoTask to Task for backend
            backend_task = Task(
                id=f"{task.file}:{task.line}",
                description=task.message,
                file_path=str(path),
                line_number=task.line,
                status="pending"
            )

            # Determine fallbacks based on primary backend
            if self.backend == "litellm-proxy":
                fallbacks = ["ollama", "aider"]
            elif self.backend == "ollama":
                fallbacks = ["aider"]
            elif self.backend == "aider":
                fallbacks = ["ollama"]
            else:
                fallbacks = ["litellm-proxy", "ollama", "aider"]

            backend = FallbackBackend(
                primary=self.backend,
                fallbacks=fallbacks,
                proxy_url=self.proxy_url,
                dry_run=self.dry_run,
                retry_attempts=self.retry_attempts
            )
            result = backend.fix(backend_task)
            return result.success

        except ImportError as e:
            print(f"   ⚠️  Backend not available: {e}")
            return False
        except Exception as e:
            print(f"   ✗ Backend error: {e}")
            return False

    def fix_all(self, todo_path: str | Path) -> HybridResult:
        """Run both phases: mechanical then LLM.

        Returns:
            HybridResult with both phases' results and timing
        """
        start = time.perf_counter()

        # Phase 1: Mechanical
        mechanical = self.fix_mechanical(todo_path)

        # Phase 2: LLM
        llm = self.fix_complex(todo_path)

        total = time.perf_counter() - start

        return HybridResult(
            mechanical=mechanical,
            llm=llm,
            total_time_sec=total,
            cost_estimate=self.total_cost
        )

    def print_summary(self, result: HybridResult | dict) -> None:
        """Print formatted summary of hybrid fix results."""
        print(f"\n{'═' * 70}")
        print("  HYBRID AUTOFIX SUMMARY")
        print(f"{'═' * 70}")

        # Handle both HybridResult dataclass and plain dict
        if isinstance(result, dict):
            # LLM-only mode returns dict
            m = {"fixed": 0, "skipped": 0, "errors": 0}
            l = result
            total_time = l.get("time", 0.0)
            cost = 0.0
        else:
            # Full hybrid mode returns HybridResult
            m = result.mechanical
            l = result.llm
            total_time = result.total_time_sec
            cost = result.cost_estimate

        print(f"\n  🔧 Mechanical Fixes:")
        print(f"     Fixed:   {m.get('fixed', 0)}")
        print(f"     Skipped: {m.get('skipped', 0)}")
        print(f"     Errors:  {m.get('errors', 0)}")

        print(f"\n  🤖 LLM Fixes:")
        print(f"     Fixed:   {l.get('fixed', 0)}")
        print(f"     Skipped: {l.get('skipped', 0)}")
        print(f"     Errors:  {l.get('errors', 0)}")
        print(f"     Calls:   {self.llm_calls}")
        print(f"     Failed:  {self.llm_errors}")

        print(f"\n  ⏱️  Total Time: {total_time:.3f}s")
        print(f"  💰 Est. Cost:  ${cost:.4f}")

        total_tasks = (m.get('fixed', 0) + m.get('skipped', 0) +
                      l.get('fixed', 0) + l.get('skipped', 0))
        if total_tasks > 0 and total_time > 0:
            throughput = total_tasks / total_time
            print(f"  ⚡ Throughput: {throughput:.1f} tickets/sec")

        print(f"{'═' * 70}")
