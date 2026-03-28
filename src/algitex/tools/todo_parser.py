"""Todo parser — read tasks from Markdown and text files.

Supports formats:
- GitHub-style: `- [ ] task` / `- [x] task`
- Prefact-style: `file.py:10 - description`
- Plain text lists

Usage:
    from algitex.tools.todo_parser import TodoParser, Task

    parser = TodoParser("TODO.md")
    tasks = parser.parse()  # List of pending Task objects
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re


@dataclass
class Task:
    """Single todo task extracted from file."""
    id: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    status: str = "pending"  # pending | completed | in_progress
    priority: Optional[str] = None
    source_file: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "status": self.status,
            "priority": self.priority,
        }


class TodoParser:
    """Parse todo lists from Markdown and text files."""

    # GitHub-style checkbox: `- [ ] task` or `* [ ] task` or `1. [ ] task`
    GITHUB_PATTERN = re.compile(
        r'^(?:\s*[-*]|\s*\d+\.)\s*\[([ xX])\]\s*(.+)$',
        re.MULTILINE
    )

    # Prefact-style: `file.py:10 - description` or `file.py:10: description`
    PREFACT_PATTERN = re.compile(
        r'^-?\s*\[?([ xX])?\]?\s*(\S+\.\w+):(\d+)\s*[-:]\s*(.+)$',
        re.MULTILINE
    )

    # Generic list item with optional priority: `- [P0] task` or `* task`
    GENERIC_PATTERN = re.compile(
        r'^(?:\s*[-*]|\s*\d+\.)\s*(?:\[([Pp]\d|[Hh]igh|[Ll]ow|[Mm]edium|[Cc]ritical)\]\s*)?(.+)$',
        re.MULTILINE
    )

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._counter = 0

    def parse(self) -> list[Task]:
        """Parse file and return list of pending tasks."""
        if not self.file_path.exists():
            return []

        content = self.file_path.read_text(encoding='utf-8')
        tasks = []

        # Try prefact format first (most specific)
        tasks.extend(self._parse_prefact(content))

        # Then GitHub checkbox format
        tasks.extend(self._parse_github(content))

        # Fallback to generic format
        tasks.extend(self._parse_generic(content))

        # Set source file on all tasks
        for t in tasks:
            t.source_file = str(self.file_path)

        return [t for t in tasks if t.status == "pending"]

    def _parse_prefact(self, content: str) -> list[Task]:
        """Parse prefact-style: `file.py:10 - description`."""
        tasks = []
        seen = set()

        for match in self.PREFACT_PATTERN.finditer(content):
            checkbox = match.group(1) or ' '
            file_path = match.group(2)
            line_no = int(match.group(3))
            desc = match.group(4).strip()

            key = f"{file_path}:{line_no}:{desc}"
            if key in seen:
                continue
            seen.add(key)

            self._counter += 1
            task = Task(
                id=f"TASK-{self._counter:03d}",
                description=desc,
                file_path=file_path,
                line_number=line_no,
                status="completed" if checkbox.lower() == 'x' else "pending",
            )
            tasks.append(task)

        return tasks

    def _parse_github(self, content: str) -> list[Task]:
        """Parse GitHub-style checkboxes."""
        tasks = []
        seen = set()

        for match in self.GITHUB_PATTERN.finditer(content):
            checkbox = match.group(1).lower()
            desc = match.group(2).strip()

            if desc in seen:
                continue
            seen.add(desc)

            # Extract file/line info from description if present
            file_path, line_no = self._extract_location(desc)

            self._counter += 1
            task = Task(
                id=f"TASK-{self._counter:03d}",
                description=desc,
                file_path=file_path,
                line_number=line_no,
                status="completed" if checkbox == 'x' else "pending",
            )
            tasks.append(task)

        return tasks

    def _parse_generic(self, content: str) -> list[Task]:
        """Parse generic list items."""
        tasks = []
        seen = set()

        for match in self.GENERIC_PATTERN.finditer(content):
            priority = match.group(1)
            desc = match.group(2).strip()

            # Skip if already parsed or looks like a header
            if desc in seen or desc.startswith('#') or desc.startswith('---'):
                continue
            seen.add(desc)

            # Extract file/line info from description if present
            file_path, line_no = self._extract_location(desc)

            self._counter += 1
            task = Task(
                id=f"TASK-{self._counter:03d}",
                description=desc,
                file_path=file_path,
                line_number=line_no,
                status="pending",
                priority=priority.lower() if priority else None,
            )
            tasks.append(task)

        return tasks

    def _extract_location(self, desc: str) -> tuple[Optional[str], Optional[int]]:
        """Try to extract file path and line number from description."""
        # Match patterns like:
        # - src/file.py:123 - description
        # - file.py:123: description
        # - in src/file.py at line 123
        patterns = [
            r'^(\S+\.\w+):(\d+)\s*[-:]\s*',
            r'in\s+(\S+\.\w+)(?:\s+at\s+line\s+|\s*:?\s*l?)(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                return match.group(1), int(match.group(2))

        return None, None

    def get_stats(self) -> dict:
        """Get statistics about parsed tasks."""
        all_tasks = self.parse()
        pending = [t for t in all_tasks if t.status == "pending"]
        completed = [t for t in all_tasks if t.status == "completed"]

        return {
            "total": len(all_tasks),
            "pending": len(pending),
            "completed": len(completed),
            "with_location": len([t for t in all_tasks if t.file_path]),
        }
