"""Parallel auto-fixer for prefact TODO tasks — Orchestrator only.

Groups tasks by file, fixes each file independently in parallel.
No merge conflicts because each worker touches a different file.

Usage:
    from algitex.todo.fixer import parallel_fix
    parallel_fix("TODO.md", workers=8, dry_run=True)
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from algitex.todo.classify import classify_message
from algitex.todo.repair import REPAIRERS, repair_fstring, repair_magic_number, repair_module_block
from algitex.todo.verifier import TodoTask

CONSTANT_3 = 3
CONSTANT_6 = 6
CONSTANT_8 = 8
CONSTANT_60 = 60


CONSTANT_3 = CONSTANT_3
CONSTANT_6 = CONSTANT_6
CONSTANT_8 = CONSTANT_8
CONSTANT_60 = CONSTANT_60


CONSTANT_3 = CONSTANT_3
CONSTANT_6 = CONSTANT_6
CONSTANT_8 = CONSTANT_8
CONSTANT_60 = CONSTANT_60


CONSTANT_3 = CONSTANT_3
CONSTANT_6 = CONSTANT_6
CONSTANT_8 = CONSTANT_8
CONSTANT_60 = CONSTANT_60


if TYPE_CHECKING:
    pass

# FIXERS is an alias for REPAIRERS for backward compatibility
FIXERS = REPAIRERS


@dataclass
class FixResult:
    """Result of fixing a file."""
    file: str
    fixed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


# ─── Parser ─────────────────────────────────────────

def parse_todo(todo_path: str | Path) -> list[TodoTask]:
    """Parse TODO.md → list of tasks, filtering worktree duplicates."""
    todo_path = Path(todo_path).resolve()
    tasks = []
    text = todo_path.read_text()

    for line in text.splitlines():
        if not line.startswith("- [ ] "):
            continue

        content = line[CONSTANT_6:]  # strip "- [ ] "
        match = re.match(r"(.+?):(\d+) - (.+)", content)
        if not match:
            continue

        file_path, lineno, message = match.group(1), int(match.group(2)), match.group(CONSTANT_3)

        # Skip worktree duplicates
        if "worktrees" in file_path or "my-app/my-app" in file_path:
            continue

        resolved_path = str((todo_path.parent / file_path).resolve())
        task = TodoTask(file=resolved_path, line=lineno, message=message)
        task.category = _categorize(message)
        tasks.append(task)

    return tasks


def _categorize(message: str) -> str:
    """Categorize a task message."""
    return classify_message(message).category


# ─── Statistics ─────────────────────────────────────

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


# ─── Reporting ──────────────────────────────────────

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
        fixable = "✓ auto" if cat in REPAIRERS else "○ manual"
        print(f"  {count:>4} {cat:<20} {fixable}")

    print("\nTiers:")
    for tier, count in sorted(tiers.items(), key=lambda x: (-x[1], x[0])):
        if count == 0:
            continue
        label = {"algorithm": "Algorithm", "micro": "Small LLM", "big": "Big LLM"}.get(tier, tier.title())
        print(f"  {count:>4} {label:<20}")

    auto_fixable = sum(1 for t in tasks if classify_message(t.message).tier == "algorithm")
    if tasks:
        pct = auto_fixable * 100 // len(tasks)
        print(f"\nAuto-fixable: {auto_fixable}/{len(tasks)} ({pct}%)")
    print(f"Files to process: {len(by_file)}")
    print(f"Workers: {workers}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")

    if dry_run:
        print("─" * CONSTANT_60)


def _print_execution_summary(
    total_fixed: int,
    total_skipped: int,
    total_errors: int,
    dry_run: bool
) -> None:
    """Print final execution summary."""
    print(f"\n{'═' * CONSTANT_60}")
    print(f"  Fixed:   {total_fixed}")
    print(f"  Skipped: {total_skipped} (need manual fix)")
    print(f"  Errors:  {total_errors}")
    print(f"{'═' * CONSTANT_60}")

    if dry_run and total_fixed > 0:
        print(f"\nRun with dry_run=False to apply {total_fixed} fixes")


# ─── Core fixer ─────────────────────────────────────

def _validate_file_with_vallm(path: Path, original_content: str) -> tuple[bool, str]:
    """Validate file with syntax check first, then vallm. Restore original if invalid.
    
    Returns:
        (is_valid, message)
    """
    # ALWAYS check syntax first - this is the most reliable check
    try:
        import ast
        ast.parse(path.read_text())
    except SyntaxError as se:
        # Restore original content immediately
        path.write_text(original_content)
        return False, f"syntax error: {se}"
    except Exception as e:
        path.write_text(original_content)
        return False, f"parse error: {e}"
    
    # If syntax is OK, try vallm for deeper validation
    try:
        from algitex.tools.analysis import Analyzer
        analyzer = Analyzer(str(path.parent))
        report = analyzer.health()
        
        # vallm_pass_rate should be > 0 for valid code
        if report.vallm_pass_rate > 0:
            return True, "valid"
        else:
            # Restore original content
            path.write_text(original_content)
            return False, f"vallm failed (pass_rate: {report.vallm_pass_rate:.2f})"
            
    except Exception:
        # If vallm unavailable, syntax check is sufficient
        return True, "syntax OK"


def fix_file(file_path: str, tasks: list[TodoTask], dry_run: bool = True) -> FixResult:
    """Fix all tasks in a single file using strategy dispatch.
    
    CC: 6 (dispatcher + loop + 4 category handlers)
    Validates with vallm after each fix, restores if invalid.
    """
    path = Path(file_path)
    result = FixResult(file=file_path)

    if not path.exists():
        result.errors.append("file not found")
        return result

    # Save original content for potential restore
    original_content = path.read_text()

    # Sort tasks by line number DESCENDING — fix bottom-up to preserve line numbers
    sorted_tasks = sorted(tasks, key=lambda t: t.line, reverse=True)

    # Group by category
    line_tasks = [t for t in sorted_tasks if t.category in {"unused_import", "return_type"}]
    magic_tasks = [t for t in sorted_tasks if t.category in {"magic", "magic_known"}]
    fstring_tasks = [t for t in sorted_tasks if t.category == "fstring"]
    exec_tasks = [t for t in sorted_tasks if t.category in {"exec_block", "module_block"}]
    other_tasks = [t for t in sorted_tasks if t.category not in REPAIRERS]

    # Process line-based fixes with validation after each
    for task in line_tasks:
        repairer = REPAIRERS.get(task.category)
        if not repairer:
            result.skipped += 1
            continue

        if dry_run:
            print(f"  [DRY] {task.file}:{task.line} — {task.category}")
            result.fixed += 1
            continue

        try:
            # Extract additional params from message
            if task.category == "unused_import":
                match = re.search(r"Unused (\w+)", task.message)
                name = match.group(1) if match else ""
                ok = repairer(path, name, task.line - 1)
            elif task.category == "return_type":
                suggested = _extract_return_type(task.message)
                ok = repairer(path, suggested or "-> None", task.line - 1)
            else:
                ok = repairer(path, "", task.line - 1)
            
            if ok:
                # Validate with vallm after fix
                is_valid, msg = _validate_file_with_vallm(path, original_content)
                if is_valid:
                    result.fixed += 1
                    print(f"    ✓ validated: {msg}")
                else:
                    result.errors.append(f"L{task.line}: fix invalid - {msg}")
                    result.skipped += 1
                    print(f"    ✗ L{task.line}: fix broke file - {msg}")
                    print(f"      ↺ ROLLBACK: file restored to original state")
                    print(f"      ⊘ SKIPPED: task abandoned")
                    # Update original_content to the restored state
                    original_content = path.read_text()
            else:
                result.skipped += 1
        except Exception as e:
            result.errors.append(f"L{task.line}: {e}")
            result.skipped += 1

    # Count other tasks as skipped
    result.skipped += len(other_tasks)

    # Process magic number fixes with validation
    if magic_tasks:
        _process_magic_batch(path, magic_tasks, result, dry_run, original_content)

    # Process fstring fixes with validation
    if fstring_tasks:
        _process_fstring_batch(path, fstring_tasks, result, dry_run, original_content)

    # Process exec block fixes with validation
    if exec_tasks:
        _process_exec_batch(path, exec_tasks, result, dry_run, original_content)

    return result


def _extract_return_type(message: str) -> str | None:
    """Extract return type annotation from message."""
    match = re.search(r"suggested:\s*(->\s*\w+)", message)
    if match:
        return match.group(1)
    explicit = re.search(r"(->\s*[A-Za-z_][A-Za-z0-9_\[\], ]*)", message)
    if explicit:
        return explicit.group(1).strip()
    return None


def _process_magic_batch(path: Path, tasks: list[TodoTask], result: FixResult, dry_run: bool, original_content: str) -> None:
    """Process magic number fixes as a batch with validation."""
    from algitex.todo.classify import KNOWN_MAGIC_CONSTANTS
    
    if dry_run:
        for task in tasks:
            match = re.search(r"\b(\d+)\b", task.message)
            number = int(match.group(1)) if match else None
            status = "fixed" if number in KNOWN_MAGIC_CONSTANTS else "skipped"
            print(f"  [DRY] {task.file}:{task.line} — magic ({status})")
            if status == "fixed":
                result.fixed += 1
            else:
                result.skipped += 1
        return

    for task in tasks:
        match = re.search(r"\b(\d+)\b", task.message)
        if not match:
            result.skipped += 1
            continue
        
        number = int(match.group(1))
        const_name = KNOWN_MAGIC_CONSTANTS.get(number)
        
        try:
            if repair_magic_number(path, number, task.line - 1, const_name):
                is_valid, msg = _validate_file_with_vallm(path, original_content)
                if is_valid:
                    result.fixed += 1
                    print(f"    ✓ magic L{task.line}: validated: {msg}")
                else:
                    result.errors.append(f"magic L{task.line}: invalid - {msg}")
                    result.skipped += 1
                    print(f"    ✗ magic L{task.line}: fix broke file - {msg}")
                    print(f"      ↺ ROLLBACK: file restored to original state")
                    print(f"      ⊘ SKIPPED: task abandoned")
                    original_content = path.read_text()
            else:
                result.skipped += 1
        except Exception as e:
            result.errors.append(f"magic L{task.line}: {e}")
            result.skipped += 1


def _process_fstring_batch(path: Path, tasks: list[TodoTask], result: FixResult, dry_run: bool, original_content: str) -> None:
    """Process fstring fixes as a batch with validation."""
    if dry_run:
        for task in tasks:
            print(f"  [DRY] {task.file}:{task.line} — fstring")
        result.fixed += len(tasks)
        return

    try:
        if repair_fstring(path):
            is_valid, msg = _validate_file_with_vallm(path, original_content)
            if is_valid:
                result.fixed += len(tasks)
                print(f"    ✓ fstring: validated: {msg}")
            else:
                result.errors.append(f"fstring: invalid - {msg}")
                result.skipped += len(tasks)
                print(f"    ✗ fstring: fix broke file - {msg}")
                print(f"      ↺ ROLLBACK: file restored to original state")
                print(f"      ⊘ SKIPPED: {len(tasks)} task(s) abandoned")
                path.write_text(original_content)
        else:
            result.skipped += len(tasks)
    except Exception as e:
        result.errors.append(f"fstring: {e}")
        result.skipped += len(tasks)


def _process_exec_batch(path: Path, tasks: list[TodoTask], result: FixResult, dry_run: bool, original_content: str) -> None:
    """Process exec block fixes as a batch with validation."""
    if dry_run:
        for task in tasks:
            print(f"  [DRY] {task.file}:{task.line} — exec_block")
        result.fixed += len(tasks)
        return

    try:
        if repair_module_block(path):
            is_valid, msg = _validate_file_with_vallm(path, original_content)
            if is_valid:
                result.fixed += len(tasks)
                print(f"    ✓ exec_block: validated: {msg}")
            else:
                result.errors.append(f"exec_block: invalid - {msg}")
                result.skipped += len(tasks)
                print(f"    ✗ exec_block: fix broke file - {msg}")
                print(f"      ↺ ROLLBACK: file restored to original state")
                print(f"      ⊘ SKIPPED: {len(tasks)} task(s) abandoned")
                path.write_text(original_content)
        else:
            result.skipped += len(tasks)
    except Exception as e:
        result.errors.append(f"exec_block: {e}")
        result.skipped += len(tasks)


# ─── Parallel executor ────────────────────────────────

def _execute_parallel_fixes(
    by_file: dict[str, list[TodoTask]],
    workers: int,
    dry_run: bool
) -> tuple[int, int, int]:
    """Execute fixes in parallel using ThreadPoolExecutor."""
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
                    print(f"  ✓ {file_path}: {result.fixed} fixed")
                if result.errors:
                    for err in result.errors:
                        print(f"  ✗ {file_path}: {err}")
            except Exception as e:
                print(f"  ✗ {file_path}: {e}")
                total_errors += 1

    return total_fixed, total_skipped, total_errors


def parallel_fix(
    todo_path: str | Path,
    workers: int = CONSTANT_8,
    dry_run: bool = True,
    category_filter: str | None = None,
    categories: set[str] | None = None,
    tasks: list[TodoTask] | None = None,
) -> dict[str, int]:
    """Fix all TODO tasks in parallel, one worker per file."""
    if tasks is None:
        tasks = parse_todo(todo_path)
        print(f"Parsed {len(tasks)} tasks (excluding worktree duplicates)\n")

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

    # Execute in parallel
    total_fixed, total_skipped, total_errors = _execute_parallel_fixes(by_file, workers, dry_run)

    # Print final summary
    _print_execution_summary(total_fixed, total_skipped, total_errors, dry_run)

    return {"fixed": total_fixed, "skipped": total_skipped, "errors": total_errors}


def mark_tasks_completed(todo_path: str | Path, completed_tasks: list[TodoTask]) -> int:
    """Mark completed tasks in TODO.md by changing - [ ] to - [x]."""
    todo_path = Path(todo_path)
    if not todo_path.exists():
        return 0

    text = todo_path.read_text()
    marked = 0

    for task in completed_tasks:
        pattern = rf"^- \[ \] {re.escape(task.file)}:{task.line} - {re.escape(task.message)}$"
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
    workers: int = CONSTANT_8,
    dry_run: bool = True,
    category_filter: str | None = None,
    categories: set[str] | None = None,
    tasks: list[TodoTask] | None = None,
) -> dict[str, int]:
    """Fix tasks and update TODO.md to mark completed tasks."""
    result = parallel_fix(todo_path, workers, dry_run, category_filter, categories, tasks)

    if not dry_run and result["fixed"] > 0:
        if tasks is None:
            tasks = parse_todo(todo_path)
        if category_filter:
            tasks = [t for t in tasks if t.category == category_filter]
        if categories:
            tasks = [t for t in tasks if t.category in categories]

        # Filter to only deterministic tasks (algorithm tier)
        fixable_tasks = [t for t in tasks if classify_message(t.message).tier == "algorithm"]
        mark_tasks_completed(todo_path, fixable_tasks[:result["fixed"]])

    return result


__all__ = [
    "TodoTask",
    "FixResult",
    "parse_todo",
    "fix_file",
    "parallel_fix",
    "parallel_fix_and_update",
    "mark_tasks_completed",
    "FIXERS",
]
