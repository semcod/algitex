"""TODO verification pipeline — check tasks against actual code state.

Splits todo_verify_prefact into 4-step pipeline:
1. _run_prefact_scan() → raw_issues
2. _parse_todo_file() → existing_tasks
3. _diff_issues() → VerifyResult
4. _format_verify_report() → str
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VerifyResult:
    """Result of TODO verification."""
    still_open: int = 0
    already_fixed: int = 0
    new_issues: int = 0
    invalid: int = 0
    details: list[dict[str, Any]] = field(default_factory=list)
    valid_tasks: list[dict[str, Any]] = field(default_factory=list)
    outdated_tasks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TodoTask:
    """Single TODO task entry."""
    status: str
    file: str
    line: int
    message: str
    original_line: str


def verify_todos(
    todo_path: str = "TODO.md",
    project_path: str = ".",
) -> VerifyResult:
    """Pipeline: scan → parse → diff → result.
    
    CC: 5 (4 pipeline steps + 1 orchestrator)
    """
    raw = _run_prefact_scan(project_path)
    existing = _parse_todo_file(todo_path)
    return _diff_issues(raw, existing)


def _run_prefact_scan(project_path: str) -> list[dict[str, Any]]:
    """Run prefact and parse its output into structured issues.
    
    CC: 3 (try/except + subprocess + json parse)
    """
    try:
        result = subprocess.run(
            ["prefact", "scan", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=project_path,
            timeout=60,
        )
        if result.returncode != 0:
            return []
        import json
        data = json.loads(result.stdout)
        return data.get("issues", []) if isinstance(data, dict) else []
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        return []


def _parse_todo_file(todo_path: str) -> list[TodoTask]:
    """Parse TODO.md into structured tasks.
    
    CC: 3 (file read + loop + regex match)
    """
    path = Path(todo_path)
    if not path.exists():
        return []
    
    tasks = []
    for line in path.read_text().splitlines():
        match = re.match(r"- \[([ x])\] (.+):(\d+) - (.+)", line)
        if match:
            status, filepath, lineno, message = match.groups()
            tasks.append(TodoTask(
                status=status,
                file=filepath,
                line=int(lineno),
                message=message,
                original_line=line,
            ))
    return tasks


def _diff_issues(raw: list[dict[str, Any]], existing: list[TodoTask]) -> VerifyResult:
    """Compare current scan vs existing TODO tasks.
    
    CC: 4 (lookup building + set ops + validation + result build)
    """
    result = VerifyResult()
    
    # Build lookups
    raw_keys = {f"{i.get('file')}:{i.get('line')}" for i in raw}
    existing_lookup = {f"{t.file}:{t.line}": t for t in existing if t.status != 'x'}
    existing_keys = set(existing_lookup.keys())
    
    # Categorize
    result.still_open = len(raw_keys & existing_keys)
    result.already_fixed = len(existing_keys - raw_keys)
    result.new_issues = len(raw_keys - existing_keys)
    
    # Validate tasks
    for task in existing:
        is_invalid = "worktrees" in task.file or "my-app/my-app" in task.file
        if is_invalid:
            result.invalid += 1
            result.outdated_tasks.append({
                "file": task.file,
                "line": task.line,
                "message": task.message,
                "reason": "invalid path",
            })
        elif _validate_task_against_file(task):
            result.valid_tasks.append({
                "file": task.file,
                "line": task.line,
                "message": task.message,
            })
        else:
            result.outdated_tasks.append({
                "file": task.file,
                "line": task.line,
                "message": task.message,
                "reason": "no longer valid",
            })
    
    return result


def _validate_task_against_file(task: TodoTask) -> bool:
    """Check if task issue still exists in the file.
    
    CC: 4 (file check + line check + keyword heuristics)
    """
    try:
        path = Path(task.file)
        if not path.exists():
            return False
        
        lines = path.read_text().splitlines()
        line_idx = task.line - 1
        
        if line_idx >= len(lines):
            return False
        
        line_content = lines[line_idx]
        msg_lower = task.message.lower()
        
        # Heuristics for different issue types
        if "unused" in msg_lower and "import" in msg_lower:
            return "import" in line_content
        elif "f-string" in msg_lower or "string concatenation" in msg_lower:
            return '"' in line_content or "'" in line_content
        elif "magic number" in msg_lower:
            return bool(re.search(r'\b\d+\b', line_content))
        
        return True
    except Exception:
        return True  # Assume valid if we can't check


def _format_verify_report(result: VerifyResult) -> str:
    """Format verification result as human-readable report.
    
    CC: 2 (header + details)
    """
    lines = [
        "TODO Verification Results",
        "=" * 40,
        f"Still open:     {result.still_open}",
        f"Already fixed:  {result.already_fixed}",
        f"New issues:     {result.new_issues}",
        f"Invalid tasks:  {result.invalid}",
        "",
    ]
    
    if result.outdated_tasks:
        lines.append("Outdated tasks:")
        for task in result.outdated_tasks[:5]:
            lines.append(f"  - {task['file']}:{task['line']} - {task['message'][:50]}")
        if len(result.outdated_tasks) > 5:
            lines.append(f"  ... and {len(result.outdated_tasks) - 5} more")
        lines.append("")
    
    return "\n".join(lines)


def prune_outdated_tasks(todo_path: str, result: VerifyResult | None = None) -> int:
    """Remove outdated tasks from TODO.md.
    
    Args:
        todo_path: Path to TODO.md
        result: Optional pre-computed VerifyResult
    
    Returns:
        Number of tasks removed
    """
    if result is None:
        result = verify_todos(todo_path)
    
    if not result.outdated_tasks:
        return 0
    
    path = Path(todo_path)
    content = path.read_text()
    
    for task in result.outdated_tasks:
        # Remove the line for this task
        pattern = rf"- \[[ x]\] {re.escape(task['file'])}:{task['line']} - {re.escape(task['message'][:100])}.*\n"
        content = re.sub(pattern, "", content)
    
    path.write_text(content)
    return len(result.outdated_tasks)


__all__ = [
    "VerifyResult",
    "TodoTask",
    "verify_todos",
    "prune_outdated_tasks",
    "_format_verify_report",
]
