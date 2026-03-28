"""Classification helpers for prefact TODO lines."""

from __future__ import annotations

import re
from pathlib import Path

from algitex.microtask import MicroTask, TaskType


KNOWN_MAGIC_NUMBERS: set[int] = {
    200,
    404,
    429,
    500,
    8080,
    8001,
    8002,
    4000,
    11434,
    120,
    30,
    150,
    5000,
}

_TASK_LINE_RE = re.compile(r"^\s*-\s*\[(?P<state>[ xX])\]\s*(?P<body>.+)$")
_LOCATION_RE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+)\s*[-:]\s*(?P<message>.+)$")
_FUNCTION_RE = re.compile(
    r"(?:function|method|class|helper)\s+`?([A-Za-z_][A-Za-z0-9_]*)`?",
    re.IGNORECASE,
)
_SUGGESTION_RE = re.compile(r"\(suggested:\s*(.+?)\)", re.IGNORECASE)
_NUMBER_RE = re.compile(r"\b(\d+)\b")


def classify_prefact_line(
    line: str,
    task_id: int,
    base_dir: str | Path | None = None,
) -> MicroTask | None:
    """Convert one prefact-style TODO line into a MicroTask."""
    match = _TASK_LINE_RE.match(line.strip())
    if not match or match.group("state").lower() == "x":
        return None

    body = match.group("body").strip()
    location = _LOCATION_RE.match(body)
    if not location:
        return None

    raw_file = location.group("file").strip()
    line_number = int(location.group("line"))
    message = location.group("message").strip()

    if _is_ignored_path(raw_file):
        return None

    task_type = _classify_message(message)
    number = _first_int(message)
    if task_type == TaskType.KNOWN_MAGIC and number is not None and number not in KNOWN_MAGIC_NUMBERS:
        task_type = TaskType.UNKNOWN_MAGIC
    if task_type == TaskType.UNKNOWN_MAGIC and number is not None and number in KNOWN_MAGIC_NUMBERS:
        task_type = TaskType.KNOWN_MAGIC

    resolved_file = _resolve_file(raw_file, base_dir)
    function_name = _extract_function_name(message)
    suggested_fix = _extract_suggestion(message)

    return MicroTask(
        id=f"MT-{task_id:04d}",
        type=task_type,
        file=str(resolved_file),
        line_start=line_number,
        line_end=line_number,
        function_name=function_name,
        prefact_message=message,
        suggested_fix=suggested_fix,
        expected_format="name" if task_type == TaskType.UNKNOWN_MAGIC else "code",
    )


def classify_todo_file(path: str | Path) -> list[MicroTask]:
    """Parse a TODO file and return the MicroTask view."""
    todo_path = Path(path)
    if not todo_path.exists():
        return []

    base_dir = todo_path.parent
    tasks: list[MicroTask] = []
    seen: set[tuple[str, int, str]] = set()

    for index, line in enumerate(todo_path.read_text(encoding="utf-8").splitlines(), start=1):
        task = classify_prefact_line(line, index, base_dir=base_dir)
        if task is None:
            continue
        key = (task.file, task.line_start, task.prefact_message)
        if key in seen:
            continue
        seen.add(key)
        tasks.append(task)
    return tasks


def _classify_message(message: str) -> TaskType:
    lowered = message.lower()

    if "unused import" in lowered or ("unused" in lowered and "import" in lowered):
        return TaskType.UNUSED_IMPORT
    if "return type" in lowered or "missing return" in lowered or "type annotation" in lowered:
        return TaskType.RETURN_TYPE
    if (
        "f-string" in lowered
        or "string concatenation" in lowered
        or "can be converted to f-string" in lowered
        or "module execution block" in lowered
        or "if __name__" in lowered
    ):
        return TaskType.FSTRING
    if "magic number" in lowered or "named constant" in lowered or ("constant" in lowered and _first_int(message) is not None):
        return TaskType.KNOWN_MAGIC
    if "sort import" in lowered or "import order" in lowered or "reorder imports" in lowered:
        return TaskType.SORT_IMPORTS
    if "trailing whitespace" in lowered or "strip whitespace" in lowered:
        return TaskType.TRAILING_WHITESPACE
    if "docstring" in lowered or "sphinx" in lowered:
        return TaskType.DOCSTRING_FIX
    if "rename" in lowered or "descriptive name" in lowered or "variable name" in lowered:
        return TaskType.VARIABLE_RENAME
    if "guard clause" in lowered or "input validation" in lowered or "validate" in lowered:
        return TaskType.GUARD_CLAUSE
    if "type hint" in lowered or "type inference" in lowered or "annotation" in lowered:
        return TaskType.TYPE_INFERENCE
    if "dispatch" in lowered or "if/elif" in lowered or "dictionary" in lowered:
        return TaskType.DICT_DISPATCH
    if "extract method" in lowered or "helper" in lowered or "repeated block" in lowered:
        return TaskType.EXTRACT_METHOD
    if "error handling" in lowered or "try/except" in lowered or "exception" in lowered:
        return TaskType.ERROR_HANDLING
    if "split" in lowered or "god function" in lowered or "too large" in lowered:
        return TaskType.SPLIT_FUNCTION
    if "dependency cycle" in lowered or "circular dependency" in lowered:
        return TaskType.DEPENDENCY_CYCLE
    if "api redesign" in lowered or "redesign" in lowered:
        return TaskType.API_REDESIGN
    return TaskType.FSTRING


def _resolve_file(file_path: str, base_dir: str | Path | None) -> Path:
    path = Path(file_path)
    if path.is_absolute() or base_dir is None:
        return path
    return (Path(base_dir) / path).resolve()


def _is_ignored_path(file_path: str) -> bool:
    normalised = file_path.replace("\\", "/")
    return normalised.startswith(".algitex/worktrees/") or normalised.startswith("my-app/")


def _first_int(text: str) -> int | None:
    match = _NUMBER_RE.search(text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _extract_function_name(message: str) -> str:
    match = _FUNCTION_RE.search(message)
    return match.group(1) if match else ""


def _extract_suggestion(message: str) -> str:
    match = _SUGGESTION_RE.search(message)
    return match.group(1).strip() if match else ""


__all__ = [
    "KNOWN_MAGIC_NUMBERS",
    "classify_prefact_line",
    "classify_todo_file",
]
