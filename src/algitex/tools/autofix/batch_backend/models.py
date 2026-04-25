from dataclasses import dataclass

from algitex.tools.autofix.base import Task


@dataclass
class TaskGroup:
    """Grupa podobnych zadań do batch fix."""

    category: str
    pattern: str
    tasks: list[Task]
    files: list[str]
