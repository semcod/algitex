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

from algitex.todo.tiering import KNOWN_MAGIC_CONSTANTS, classify_message


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
    return classify_message(message).category


# ─── Fixers per category ─────────────────────────────────


def _simple_fstring_rewrite(line: str) -> str:
    """Rewrite one simple string concatenation into an f-string."""
    pattern = re.compile(
        r'(?P<quote>["\'])'
        r'(?P<prefix>[^"\']*)'
        r'(?P=quote)\s*\+\s*'
        r'(?P<expr>[A-Za-z_][A-Za-z0-9_\.]*)\s*\+\s*'
        r'(?P<suffix>["\'])(?P<tail>[^"\']*)\4'
    )

    def _replace(match: re.Match[str]) -> str:
        prefix = match.group("prefix")
        expr = match.group("expr")
        tail = match.group("tail")
        return f'f"{prefix}{{{expr}}}{tail}"'

    return pattern.sub(_replace, line, count=1)


def _find_import_insert_point(lines: list[str]) -> int:
    """Find the insert point just after the last import statement."""
    last_import = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            last_import = i + 1
    return last_import


def _extract_magic_number(task: TodoTask) -> int | None:
    """Extract the numeric literal for a magic-number task."""
    match = re.search(r"\b(\d+)\b", task.message)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None

    line_index = task.line - 1
    try:
        line = Path(task.file).read_text().splitlines()[line_index]
    except Exception:
        return None

    match = re.search(r"\b(\d+)\b", line)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _apply_magic_number_fixes(path: Path, tasks: list[TodoTask]) -> tuple[int, int]:
    """Apply known magic-number replacements in one pass."""
    if not tasks:
        return 0, 0

    lines = path.read_text().splitlines()
    replacements: list[tuple[int, int, str]] = []
    constants_needed: dict[str, int] = {}
    fixed = 0
    skipped = 0

    for task in sorted(tasks, key=lambda t: t.line, reverse=True):
        number = _extract_magic_number(task)
        if number is None or number not in KNOWN_MAGIC_CONSTANTS:
            skipped += 1
            continue

        const_name = KNOWN_MAGIC_CONSTANTS[number]
        constants_needed[const_name] = number

        if task.line - 1 >= len(lines):
            skipped += 1
            continue

        line = lines[task.line - 1]
        new_line = re.sub(
            rf'(?<!["\'])\b{number}\b(?!["\'])',
            const_name,
            line,
            count=1,
        )
        if new_line == line:
            skipped += 1
            continue

        lines[task.line - 1] = new_line
        fixed += 1

    if fixed == 0:
        return 0, skipped

    existing_constants = set()
    for line in lines:
        match = re.match(r"^([A-Z][A-Z0-9_]+)\s*=\s*\d+\s*$", line.strip())
        if match:
            existing_constants.add(match.group(1))

    missing_constants = {
        name: value
        for name, value in constants_needed.items()
        if name not in existing_constants
    }

    if missing_constants:
        insert_at = _find_import_insert_point(lines)
        const_block = ["", "# Constants"]
        const_block.extend(f"{name} = {value}" for name, value in missing_constants.items())
        const_block.append("")
        lines[insert_at:insert_at] = const_block

    path.write_text("\n".join(lines) + "\n")
    return fixed, skipped


def _apply_fstring_fix(path: Path) -> bool:
    """Convert simple string concatenations to f-strings."""
    try:
        import shutil
        import subprocess

        if shutil.which("flynt"):
            result = subprocess.run(
                ["flynt", str(path), "--transform-concats", "--quiet"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return True
    except Exception:
        pass

    lines = path.read_text().splitlines()
    changed = False
    for index, line in enumerate(lines):
        new_line = _simple_fstring_rewrite(line)
        if new_line != line:
            lines[index] = new_line
            changed = True

    if changed:
        path.write_text("\n".join(lines) + "\n")
    return changed


def _apply_module_block_fix(path: Path) -> bool:
    """Add a module execution block if one is missing."""
    text = path.read_text()
    if "if __name__ == '__main__':" in text or 'if __name__ == "__main__":' in text:
        return False

    stripped = text.rstrip()
    if not stripped:
        return False

    if stripped.endswith("main()"):
        stripped += "\n"
    else:
        stripped += "\n\n"

    stripped += "if __name__ == '__main__':\n    main()\n"
    path.write_text(stripped)
    return True

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
    return _apply_fstring_fix(path)


def fix_magic_number(path: Path, task: TodoTask) -> bool:
    """Replace a known magic number with a named constant."""
    fixed, _ = _apply_magic_number_fixes(path, [task])
    return fixed > 0


def fix_module_block(path: Path, task: TodoTask) -> bool:
    """Add a standard `if __name__ == '__main__'` guard."""
    return _apply_module_block_fix(path)


def fix_return_type(path: Path, task: TodoTask) -> bool:
    """Add return type annotation based on suggestion."""
    suggested = None
    match = re.search(r"suggested:\s*(->\s*\w+)", task.message)
    if match:
        suggested = match.group(1)
    else:
        explicit = re.search(r"(->\s*[A-Za-z_][A-Za-z0-9_\[\], ]*)", task.message)
        if explicit:
            suggested = explicit.group(1).strip()

    if not suggested:
        if any(key in task.message.lower() for key in ("return type", "missing return", "-> none", "-> bool", "-> str", "-> int")):
            suggested = "-> None"
        else:
            return False

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
    "magic": fix_magic_number,
    "exec_block": fix_module_block,
    "module_block": fix_module_block,
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


def _compute_tier_stats(tasks: list[TodoTask]) -> dict[str, int]:
    """Compute tier statistics for tasks."""
    tiers: dict[str, int] = {"algorithm": 0, "micro": 0, "big": 0}
    for task in tasks:
        tier = classify_message(task.message).tier
        tiers[tier] = tiers.get(tier, 0) + 1
    return tiers


def _print_pre_execution_summary(
    tasks: list[TodoTask],
    by_file: dict[str, list[TodoTask]],
    workers: int,
    dry_run: bool
) -> None:
    """Print pre-execution summary with category stats."""
    cats = _compute_category_stats(tasks)
    tiers = _compute_tier_stats(tasks)

    print("Categories:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        fixable = "✓ auto" if cat in FIXERS else "○ manual"
        print(f"  {count:>4} {cat:<20} {fixable}")

    print("\nTiers:")
    for tier, count in sorted(tiers.items(), key=lambda x: (-x[1], x[0])):
        if count == 0:
            continue
        label = {
            "algorithm": "Algorithm",
            "micro": "Small LLM",
            "big": "Big LLM",
        }.get(tier, tier.title())
        print(f"  {count:>4} {label:<20}")

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

    line_tasks: list[TodoTask] = []
    magic_tasks: list[TodoTask] = []
    fstring_tasks: list[TodoTask] = []
    exec_tasks: list[TodoTask] = []
    other_tasks: list[TodoTask] = []

    for task in sorted_tasks:
        if task.category in {"unused_import", "return_type"}:
            line_tasks.append(task)
        elif task.category in {"magic"}:
            magic_tasks.append(task)
        elif task.category in {"fstring"}:
            fstring_tasks.append(task)
        elif task.category in {"exec_block", "module_block"}:
            exec_tasks.append(task)
        else:
            other_tasks.append(task)

    for task in line_tasks:
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

    if other_tasks:
        for task in other_tasks:
            result.skipped += 1

    if magic_tasks:
        if dry_run:
            for task in magic_tasks:
                number = _extract_magic_number(task)
                status = "fixed" if number in KNOWN_MAGIC_CONSTANTS else "skipped"
                print(f"  [DRY] {task.file}:{task.line} — magic: {task.message[:60]} ({status})")
                if status == "fixed":
                    result.fixed += 1
                else:
                    result.skipped += 1
        else:
            try:
                fixed, skipped = _apply_magic_number_fixes(path, magic_tasks)
                result.fixed += fixed
                result.skipped += skipped
            except Exception as e:
                result.errors.append(f"magic: {e}")
                result.skipped += len(magic_tasks)

    if fstring_tasks:
        if dry_run:
            for task in fstring_tasks:
                print(f"  [DRY] {task.file}:{task.line} — fstring: {task.message[:60]}")
            result.fixed += len(fstring_tasks)
        else:
            try:
                if _apply_fstring_fix(path):
                    result.fixed += len(fstring_tasks)
                else:
                    result.skipped += len(fstring_tasks)
            except Exception as e:
                result.errors.append(f"fstring: {e}")
                result.skipped += len(fstring_tasks)

    if exec_tasks:
        if dry_run:
            for task in exec_tasks:
                print(f"  [DRY] {task.file}:{task.line} — exec_block: {task.message[:60]}")
            result.fixed += len(exec_tasks)
        else:
            try:
                if _apply_module_block_fix(path):
                    result.fixed += len(exec_tasks)
                else:
                    result.skipped += len(exec_tasks)
            except Exception as e:
                result.errors.append(f"exec_block: {e}")
                result.skipped += len(exec_tasks)

    return result


def parallel_fix(
    todo_path: str | Path,
    workers: int = 8,
    dry_run: bool = True,
    category_filter: str | None = None,
    categories: set[str] | None = None,
    tasks: list[TodoTask] | None = None,
) -> dict[str, int]:
    """Fix all TODO tasks in parallel, one worker per file.

    Args:
        todo_path: Path to TODO.md file
        workers: Number of parallel workers
        dry_run: If True, only show what would be fixed
        category_filter: If set, only fix this category
        categories: Optional set of categories to include
        tasks: Optional pre-parsed task list to use instead of reading TODO.md

    Returns:
        Dict with counts: fixed, skipped, errors
    """
    if tasks is None:
        tasks = parse_todo(todo_path)
        print(f"Parsed {len(tasks)} tasks (excluding worktree duplicates)\n")
    else:
        print(f"Using {len(tasks)} preselected tasks\n")

    # Filter by category if requested
    if category_filter:
        tasks = [t for t in tasks if t.category == category_filter]
        print(f"Filtered to {len(tasks)} tasks of category '{category_filter}'\n")

    if categories:
        tasks = [t for t in tasks if t.category in categories]
        print(f"Filtered to {len(tasks)} tasks in categories: {', '.join(sorted(categories))}\n")

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


def mark_tasks_completed(todo_path: str | Path, completed_tasks: list[TodoTask]) -> int:
    """Mark completed tasks in TODO.md by changing - [ ] to - [x].
    
    Args:
        todo_path: Path to TODO.md file
        completed_tasks: List of tasks that were successfully fixed
        
    Returns:
        Number of tasks marked as completed
    """
    todo_path = Path(todo_path)
    if not todo_path.exists():
        return 0
    
    text = todo_path.read_text()
    marked = 0
    
    for task in completed_tasks:
        # Create pattern to match this specific task
        # Format: - [ ] file:line - message
        pattern = rf"^- \[ \] {re.escape(task.file)}:{task.line} - {re.escape(task.message)}$"
        
        # Find and replace
        new_text, count = re.subn(pattern, f"- [x] {task.file}:{task.line} - {task.message}", text, flags=re.MULTILINE)
        if count > 0:
            text = new_text
            marked += 1
    
    if marked > 0:
        todo_path.write_text(text)
        print(f"\n✓ Marked {marked} tasks as completed in TODO.md")
    
    return marked


def parallel_fix_and_update(
    todo_path: str | Path,
    workers: int = 8,
    dry_run: bool = True,
    category_filter: str | None = None,
    categories: set[str] | None = None,
    tasks: list[TodoTask] | None = None,
) -> dict[str, int]:
    """Fix tasks and update TODO.md to mark completed tasks.
    
    This is a wrapper around parallel_fix that also updates the TODO.md
    to mark successfully fixed tasks as completed.
    """
    # First, run the fix
    result = parallel_fix(
        todo_path,
        workers,
        dry_run,
        category_filter=category_filter,
        categories=categories,
        tasks=tasks,
    )
    
    # If not dry run and we fixed something, mark tasks as completed
    if not dry_run and result["fixed"] > 0:
        # Get the list of tasks that were fixed
        tasks = parse_todo(todo_path)
        if category_filter:
            tasks = [t for t in tasks if t.category == category_filter]
        if categories:
            tasks = [t for t in tasks if t.category in categories]
        
        # Filter to only FIXERS categories (mechanical fixes)
        fixable_tasks = [t for t in tasks if t.category in FIXERS]
        
        # Mark them as completed
        mark_tasks_completed(todo_path, fixable_tasks[:result["fixed"]])
    
    return result
