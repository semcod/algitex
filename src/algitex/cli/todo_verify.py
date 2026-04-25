import subprocess
import re
from pathlib import Path
from rich.console import Console

console = Console()

def todo_verify_prefact(file: str, prune: bool):
    """Verify TODO.md against actual code using prefact."""
    console.print(f"[bold]Verify TODO.md with prefact[/]: {file}")
    console.print("\n🔍 Running prefact scan...")
    try:
        result = subprocess.run(["prefact", "scan", "--format", "json"], capture_output=True, text=True, cwd=".")
        if result.returncode != 0:
            console.print(f"[yellow]⚠️  Prefact scan failed: {result.stderr}[/]")
            return
    except FileNotFoundError:
        console.print("[red]✗ prefact not installed. Install with: pip install prefact[/]")
        return

    todo_path = Path(file)
    if not todo_path.exists():
        console.print(f"[red]✗ {file} not found[/]")
        return

    todo_content = todo_path.read_text()
    todo_tasks = []
    for line in todo_content.splitlines():
        match = re.match(r"- \[([ x])\] (.+):(\d+) - (.+)", line)
        if match:
            status, filepath, lineno, message = match.groups()
            todo_tasks.append({"status": status, "file": filepath, "line": int(lineno), "message": message, "original_line": line})

    console.print(f"📋 Found {len(todo_tasks)} tasks in TODO.md")
    valid_tasks, outdated_tasks = _validate_tasks(todo_tasks)
    
    console.print(f"\n[green]✓ Valid tasks: {len(valid_tasks)}[/]")
    if outdated_tasks:
        console.print(f"[yellow]⚠️  Outdated tasks: {len(outdated_tasks)}[/]")
        for task in outdated_tasks[:5]:
            console.print(f"   - {task['file']}:{task['line']} - {task['message'][:50]}")

    if prune and outdated_tasks:
        new_content = todo_content
        for task in outdated_tasks:
            new_content = new_content.replace(task["original_line"] + "\n", "")
        todo_path.write_text(new_content)
        console.print(f"[green]✓ Removed {len(outdated_tasks)} outdated tasks from {file}[/]")
    elif prune:
        console.print("\n[green]✓ No outdated tasks to remove[/]")
    console.print(f"\n[bold]{'═' * 60}[/]")

# Dispatch table: (keyword_tuple) → validator function
_VALIDATORS: list[tuple[tuple[str, ...], callable]] = [
    (("unused", "import"), lambda line: "import" in line),
    (("f-string",), lambda line: '"' in line or "'" in line),
    (("string concatenation",), lambda line: '"' in line or "'" in line),
    (("magic number",), lambda line: bool(re.search(r'\b\d+\b', line))),
]


def _validate_tasks(tasks):
    """Validate tasks against current file content.

    CC: 4 (loop + path check + line check + dispatch)
    Was: CC 15 (nested if/elif per type)
    """
    valid, outdated = [], []
    for task in tasks:
        try:
            path = Path(task["file"])
            if not path.exists():
                outdated.append(task)
                continue
            lines = path.read_text().splitlines()
            line_no = task["line"] - 1
            if line_no >= len(lines):
                outdated.append(task)
                continue
            line_content = lines[line_no]
            msg_lower = task["message"].lower()

            is_valid = True
            for keywords, check in _VALIDATORS:
                if all(kw in msg_lower for kw in keywords):
                    is_valid = check(line_content)
                    break

            (valid if is_valid else outdated).append(task)
        except Exception:
            valid.append(task)
    return valid, outdated