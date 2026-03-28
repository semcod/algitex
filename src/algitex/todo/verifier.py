"""TODO verification - check which prefact tasks are still valid.

Usage:
    from algitex.todo.verifier import TodoVerifier
    verifier = TodoVerifier("TODO.md")
    result = verifier.verify()
    print(f"Open: {result.still_open}, Fixed: {result.already_fixed}")
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TodoTask:
    """Single TODO task from prefact output."""
    file: str
    line: int
    message: str
    original_line: str = ""


@dataclass
class VerificationResult:
    """Result of TODO verification."""
    still_open: int = 0
    already_fixed: int = 0
    invalid: int = 0
    details: list = field(default_factory=list)


class TodoVerifier:
    """Verify which TODO tasks from prefact are still valid."""

    def __init__(self, todo_path: str | Path):
        self.todo_path = Path(todo_path)
        self.result = VerificationResult()

    def parse(self) -> list[TodoTask]:
        """Parse TODO.md file into list of tasks."""
        tasks = []
        if not self.todo_path.exists():
            return tasks

        text = self.todo_path.read_text()

        for line in text.splitlines():
            if not line.startswith("- [ ] "):
                continue

            content = line[6:]  # strip "- [ ] "
            match = re.match(r"(.+?):(\d+) - (.+)", content)
            if not match:
                continue

            file_path = match.group(1)
            lineno = int(match.group(2))
            message = match.group(3)

            # Skip worktree duplicates
            if "worktrees" in file_path or "my-app/my-app" in file_path:
                continue

            tasks.append(TodoTask(
                file=file_path,
                line=lineno,
                message=message,
                original_line=line
            ))

        return tasks

    def verify(self) -> VerificationResult:
        """Verify all tasks and return result."""
        tasks = self.parse()
        self.result = VerificationResult()

        for task in tasks:
            self._verify_task(task)

        return self.result

    def _verify_task(self, task: TodoTask) -> None:
        """Verify a single task."""
        file_path = Path(task.file)

        # Check if file exists
        if not file_path.exists():
            self.result.already_fixed += 1
            self.result.details.append({
                "status": "GONE",
                "file": task.file,
                "line": task.line,
                "message": task.message
            })
            return

        # Check by issue type
        status = self._check_by_type(task)

        if status == "open":
            self.result.still_open += 1
        else:
            self.result.already_fixed += 1

    def _check_by_type(self, task: TodoTask) -> str:
        """Check task based on its category. Returns 'open' or 'fixed'."""
        msg = task.message
        file_path = Path(task.file)

        try:
            lines = file_path.read_text().splitlines()
            if task.line - 1 >= len(lines):
                return "fixed"

            line_content = lines[task.line - 1]

            # Unused import
            if "Unused import" in msg or "Unused " in msg:
                return self._check_unused_import(task, line_content)

            # f-string
            if "f-string" in msg:
                return "open" if '+ "' in line_content else "fixed"

            # Magic number
            if "Magic number" in msg:
                match = re.search(r'(\d+)', msg)
                if match:
                    magic = match.group(1)
                    return "open" if re.search(rf'\b{magic}\b', line_content) else "fixed"
                return "open"

            # Missing return type
            if "missing return type" in msg:
                return "fixed" if ' -> ' in line_content else "open"

            # Default: assume open
            return "open"

        except Exception:
            return "fixed"

    def _check_unused_import(self, task: TodoTask, line_content: str) -> str:
        """Check if unused import is still present."""
        match = re.search(r'Unused (\w+)', task.message)
        if not match:
            return "open"

        name = match.group(1)

        # Check if import is still on the line
        if re.search(rf'import.*{name}', line_content):
            return "open"
        return "fixed"

    def print_report(self) -> None:
        """Print verification report."""
        print("Weryfikacja tasków...")
        print("")

        for detail in self.result.details:
            status = detail["status"]
            file = detail["file"]
            line = detail["line"]
            message = detail["message"]

            if status == "GONE":
                print(f"  GONE: {file}")
            elif status == "open":
                print(f"  OPEN: {file}:{line} — {message[:60]}")
            else:
                print(f"  FIXED: {file}:{line}")

        print("")
        print("═" * 40)
        print(f"  Still open:    {self.result.still_open}")
        print(f"  Already fixed: {self.result.already_fixed}")
        print(f"  Invalid (dup): {self.result.invalid}")
        print("═" * 40)


def verify_todos(todo_path: str | Path = "TODO.md") -> VerificationResult:
    """Quick verification function.

    Args:
        todo_path: Path to TODO.md file

    Returns:
        VerificationResult with counts
    """
    verifier = TodoVerifier(todo_path)
    result = verifier.verify()
    verifier.print_report()
    return result
