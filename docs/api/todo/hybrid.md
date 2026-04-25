# `todo.hybrid`

Hybrid Autofix — combines fast parallel mechanical fixes with LLM-based fixes.

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


### `HybridResult`

Result of hybrid fix operation.

### `RateLimiter`

Token bucket rate limiter for LLM calls.

**Methods:**

#### `__init__`

```python
def __init__(self, rate: float=10.0, burst: int=5)
```

Initialize rate limiter.

        Args:
            rate: Maximum sustained rate (calls per second)
            burst: Maximum burst size
        

#### `acquire`

```python
def acquire(self) -> float
```

Acquire a token, return wait time if any.

### `LLMTask`

Task for LLM-based fixing.

### `HybridAutofix`

Hybrid autofix: parallel mechanical + rate-limited parallel LLM.

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
    

**Methods:**

#### `__init__`

```python
def __init__(self, backend: str='litellm-proxy', tool: str='aider', proxy_url: str='http://localhost:4000', workers: int=4, rate_limit: float=10.0, retry_attempts: int=3, timeout: float=30.0, dry_run: bool=True, audit_dir: str='.algitex/audit')
```

#### `fix_mechanical`

```python
def fix_mechanical(self, todo_path: str | Path) -> dict
```

Phase 1: Fast parallel mechanical fixes with audit logging.

#### `fix_complex`

```python
def fix_complex(self, todo_path: str | Path, include_categories: set[str] | None=None, exclude_categories: set[str] | None=None, tasks: list[TodoTask] | None=None) -> dict
```

Phase 2: Rate-limited parallel LLM fixes.

        Uses ThreadPoolExecutor with rate limiting for LLM calls.
        Throughput: ~rate_limit tickets/sec (e.g., 10/sec)

        Returns:
            Dict with fixed, skipped, errors counts
        

#### `fix_all`

```python
def fix_all(self, todo_path: str | Path) -> HybridResult
```

Run both phases with full transparency and audit logging.

        Returns:
            HybridResult with audit log path for rollback capability.
        

#### `print_summary`

```python
def print_summary(self, result: HybridResult | dict) -> None
```

Print formatted summary of hybrid fix results.
