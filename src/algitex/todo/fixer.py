"""Parallel auto-fixer for prefact TODO tasks.

Groups tasks by file, fixes each file independently in parallel.
No merge conflicts because each worker touches a different file.

Usage:
    from algitex.todo.fixer import parallel_fix
    parallel_fix("TODO.md", workers=8, dry_run=True)
"""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class TodoTask:
    """Single TODO task."""
    file: str
    line: int
    message: str
    category: str = ""  # unused_import, fstring, magic, return_type, docstring, exec_block


@dataclass
class FixResult:
    """Result of fixing a file."""
    file: str
    fixed: int = 0
    skipped: int = 0
    errors: list = field(default_factory=list)


# ─── Parser ──────────────────────────────────────────────

def parse_todo(todo_path: str | Path) -> list[TodoTask]:
    """Parse TODO.md → list of tasks, filtering out worktree duplicates.
    
    File paths in tasks are resolved relative to the TODO.md directory.
    """
    todo_path = Path(todo_path).resolve()
    tasks = []
    text = todo_path.read_text()

    for line in text.splitlines():
        if not line.startswith("- [ ] "):
            continue

        content = line[6:]  # strip "- [ ] "
        match = re.match(r"(.+?):(\d+) - (.+)", content)
        if not match:
            continue

        file_path, lineno, message = match.group(1), int(match.group(2)), match.group(3)

        # Skip worktree duplicates
        if "worktrees" in file_path or "my-app/my-app" in file_path:
            continue

        # Resolve file path relative to TODO.md directory
        resolved_path = str((todo_path.parent / file_path).resolve())
        
        task = TodoTask(file=resolved_path, line=lineno, message=message)
        task.category = _categorize(message)
        tasks.append(task)

    return tasks


def _categorize(message: str) -> str:
    """Categorize a task message."""
    if "Unused import" in message or "Unused " in message:
        return "unused_import"
    if "f-string" in message:
        return "fstring"
    if "Magic number" in message:
        return "magic"
    if "missing return type" in message:
        return "return_type"
    if "LLM-style docstring" in message:
        return "docstring"
    if "module execution block" in message:
        return "exec_block"
    return "other"


# ─── Fixers per category ─────────────────────────────────

def fix_unused_import(path: Path, task: TodoTask) -> bool:
    """Remove unused import line."""
    lines = path.read_text().splitlines()
    if task.line - 1 >= len(lines):
        return False

    line = lines[task.line - 1]

    # Extract import name from message
    match = re.search(r"Unused (\w+)", task.message)
    if not match:
        return False
    name = match.group(1)

    # Case 1: "import X" → remove entire line
    if re.match(rf"^import\s+{name}\s*$", line.strip()):
        lines.pop(task.line - 1)
        path.write_text("\n".join(lines) + "\n")
        return True

    # Case 2: "from Y import X" → remove line
    if re.match(rf"^from\s+\S+\s+import\s+{name}\s*$", line.strip()):
        lines.pop(task.line - 1)
        path.write_text("\n".join(lines) + "\n")
        return True

    # Case 3: "from Y import A, X, B" → remove X from list
    if f"import" in line and name in line:
        new_line = re.sub(rf",?\s*{name}\s*,?", ",", line)
        new_line = re.sub(r",\s*$", "", new_line)  # trailing comma
        new_line = re.sub(r"import\s*,", "import ", new_line)  # leading comma after import
        lines[task.line - 1] = new_line
        path.write_text("\n".join(lines) + "\n")
        return True

    return False


def fix_fstring(path: Path, task: TodoTask) -> bool:
    """Convert string concatenation to f-string (simple cases only)."""
    # Too complex for regex — delegate to flynt
    return False


def fix_return_type(path: Path, task: TodoTask) -> bool:
    """Add return type annotation based on suggestion."""
    match = re.search(r"suggested: (-> \w+)", task.message)
    if not match:
        return False

    suggested = match.group(1)
    lines = path.read_text().splitlines()
    if task.line - 1 >= len(lines):
        return False

    line = lines[task.line - 1]

    # Add return type before the colon
    if "def " in line and ":" in line and " -> " not in line:
        new_line = re.sub(r"\)\s*:", f") {suggested}:", line)
        lines[task.line - 1] = new_line
        path.write_text("\n".join(lines) + "\n")
        return True

    return False


FIXERS: dict[str, Callable[[Path, TodoTask], bool]] = {
    "unused_import": fix_unused_import,
    "return_type": fix_return_type,
    "fstring": fix_fstring,
}


def _group_tasks_by_file(tasks: list[TodoTask]) -> dict[str, list[TodoTask]]:
    """Group tasks by file path for parallel processing."""
    by_file: dict[str, list[TodoTask]] = {}
    for task in tasks:
        by_file.setdefault(task.file, []).append(task)
    return by_file


def _compute_category_stats(tasks: list[TodoTask]) -> dict[str, int]:
    """Compute category statistics for tasks."""
    cats: dict[str, int] = {}
    for task in tasks:
        cats[task.category] = cats.get(task.category, 0) + 1
    return cats


def _print_pre_execution_summary(
    tasks: list[TodoTask],
    by_file: dict[str, list[TodoTask]],
    workers: int,
    dry_run: bool
) -> None:
    """Print pre-execution summary with category stats."""
    cats = _compute_category_stats(tasks)

    print("Categories:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        fixable = "✓ auto" if cat in FIXERS else "○ manual"
        print(f"  {count:>4} {cat:<20} {fixable}")

    auto_fixable = sum(1 for t in tasks if t.category in FIXERS)
    if tasks:
        pct = auto_fixable * 100 // len(tasks)
        print(f"\nAuto-fixable: {auto_fixable}/{len(tasks)} ({pct}%)")
    print(f"Files to process: {len(by_file)}")
    print(f"Workers: {workers}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")

    if dry_run:
        print("─" * 60)


def _execute_parallel_fixes(
    by_file: dict[str, list[TodoTask]],
    workers: int,
    dry_run: bool
) -> tuple[int, int, int]:
    """Execute fixes in parallel using ThreadPoolExecutor.

    Returns:
        Tuple of (total_fixed, total_skipped, total_errors)
    """
    total_fixed = 0
    total_skipped = 0
    total_errors = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fix_file, file_path, file_tasks, dry_run): file_path
            for file_path, file_tasks in by_file.items()
        }

        for future in as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                total_fixed += result.fixed
                total_skipped += result.skipped
                total_errors += len(result.errors)

                if not dry_run and result.fixed > 0:
                    print(f"  ✓ {file_path}: {result.fixed} fixed, {result.skipped} skipped")
                if result.errors:
                    for err in result.errors:
                        print(f"  ✗ {file_path}: {err}")

            except Exception as e:
                print(f"  ✗ {file_path}: {e}")
                total_errors += 1

    return total_fixed, total_skipped, total_errors


def _print_execution_summary(
    total_fixed: int,
    total_skipped: int,
    total_errors: int,
    dry_run: bool
) -> None:
    """Print final execution summary."""
    print(f"\n{'═' * 60}")
    print(f"  Fixed:   {total_fixed}")
    print(f"  Skipped: {total_skipped} (need manual fix or flynt/mypy)")
    print(f"  Errors:  {total_errors}")
    print(f"{'═' * 60}")

    if dry_run and total_fixed > 0:
        print(f"\nRun with dry_run=False to apply {total_fixed} fixes")


# ─── Parallel executor ───────────────────────────────────

def fix_file(file_path: str, tasks: list[TodoTask], dry_run: bool = True) -> FixResult:
    """Fix all tasks in a single file. Safe to run in parallel per-file."""
    path = Path(file_path)
    result = FixResult(file=file_path)

    if not path.exists():
        result.errors.append("file not found")
        return result

    # Sort tasks by line number DESCENDING — fix bottom-up to preserve line numbers
    sorted_tasks = sorted(tasks, key=lambda t: t.line, reverse=True)

    for task in sorted_tasks:
        fixer = FIXERS.get(task.category)
        if not fixer:
            result.skipped += 1
            continue

        if dry_run:
            print(f"  [DRY] {task.file}:{task.line} — {task.category}: {task.message[:60]}")
            result.fixed += 1
            continue

        try:
            if fixer(path, task):
                result.fixed += 1
            else:
                result.skipped += 1
        except Exception as e:
            result.errors.append(f"L{task.line}: {e}")
            result.skipped += 1

    return result


def parallel_fix(
    todo_path: str | Path,
    workers: int = 8,
    dry_run: bool = True,
    category_filter: str | None = None
) -> dict[str, int]:
    """Fix all TODO tasks in parallel, one worker per file.

    Args:
        todo_path: Path to TODO.md file
        workers: Number of parallel workers
        dry_run: If True, only show what would be fixed
        category_filter: If set, only fix this category

    Returns:
        Dict with counts: fixed, skipped, errors
    """
    tasks = parse_todo(todo_path)
    print(f"Parsed {len(tasks)} tasks (excluding worktree duplicates)\n")

    # Filter by category if requested
    if category_filter:
        tasks = [t for t in tasks if t.category == category_filter]
        print(f"Filtered to {len(tasks)} tasks of category '{category_filter}'\n")

    # Group by file
    by_file = _group_tasks_by_file(tasks)

    # Print pre-execution summary
    _print_pre_execution_summary(tasks, by_file, workers, dry_run)

    # Execute in parallel (one worker per file — zero conflicts)
    total_fixed, total_skipped, total_errors = _execute_parallel_fixes(
        by_file, workers, dry_run
    )

    # Print final summary
    _print_execution_summary(total_fixed, total_skipped, total_errors, dry_run)

    return {
        "fixed": total_fixed,
        "skipped": total_skipped,
        "errors": total_errors
    }
