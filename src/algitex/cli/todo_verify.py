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

def _validate_tasks(tasks):
    valid, outdated = [], []
    for task in tasks:
        try:
            path = Path(task["file"])
            if not path.exists():
                outdated.append(task); continue
            lines = path.read_text().splitlines()
            line_no = task["line"] - 1
            if line_no >= len(lines): 
                outdated.append(task); continue
            line_content = lines[line_no]
            msg_lower = task["message"].lower()
            is_valid = True
            if "unused" in msg_lower and "import" in msg_lower and "import" not in line_content:
                is_valid = False
            elif ("f-string" in msg_lower or "string concatenation" in msg_lower) and not any(c in line_content for c in ['"', "'"]):
                is_valid = False
            elif "magic number" in msg_lower and not re.search(r'\b\d+\b', line_content):
                is_valid = False
            (valid if is_valid else outdated).append(task)
        except Exception:
            valid.append(task)
    return valid, outdated