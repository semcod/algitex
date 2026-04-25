"""Classification helpers for prefact TODO lines."""

from __future__ import annotations

import re
from pathlib import Path

from algitex.microtask import MicroTask, TaskType

CONSTANT_30 = 30
CONSTANT_120 = 120
CONSTANT_150 = 150
CONSTANT_200 = 200
CONSTANT_404 = 404
CONSTANT_429 = 429
CONSTANT_500 = 500
CONSTANT_4000 = 4000
CONSTANT_5000 = 5000
CONSTANT_8001 = 8001
CONSTANT_8002 = 8002
CONSTANT_8080 = 8080
CONSTANT_11434 = 11434

KNOWN_MAGIC_NUMBERS: set[int] = {
    CONSTANT_200,
    CONSTANT_404,
    CONSTANT_429,
    CONSTANT_500,
    CONSTANT_8080,
    CONSTANT_8001,
    CONSTANT_8002,
    CONSTANT_4000,
    CONSTANT_11434,
    CONSTANT_120,
    CONSTANT_30,
    CONSTANT_150,
    CONSTANT_5000,
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


# Dispatch table: (pattern, TaskType)
_CLASSIFY_PATTERNS: list[tuple[str, TaskType]] = [
    ("unused import", TaskType.UNUSED_IMPORT),
    ("return type", TaskType.RETURN_TYPE),
    ("missing return", TaskType.RETURN_TYPE),
    ("type annotation", TaskType.RETURN_TYPE),
    ("f-string", TaskType.FSTRING),
    ("string concatenation", TaskType.FSTRING),
    ("module execution block", TaskType.FSTRING),
    ("if __name__", TaskType.FSTRING),
    ("magic number", TaskType.KNOWN_MAGIC),
    ("named constant", TaskType.KNOWN_MAGIC),
    ("sort import", TaskType.SORT_IMPORTS),
    ("import order", TaskType.SORT_IMPORTS),
    ("reorder imports", TaskType.SORT_IMPORTS),
    ("trailing whitespace", TaskType.TRAILING_WHITESPACE),
    ("strip whitespace", TaskType.TRAILING_WHITESPACE),
    ("docstring", TaskType.DOCSTRING_FIX),
    ("sphinx", TaskType.DOCSTRING_FIX),
    ("rename", TaskType.VARIABLE_RENAME),
    ("descriptive name", TaskType.VARIABLE_RENAME),
    ("variable name", TaskType.VARIABLE_RENAME),
    ("guard clause", TaskType.GUARD_CLAUSE),
    ("input validation", TaskType.GUARD_CLAUSE),
    ("type hint", TaskType.TYPE_INFERENCE),
    ("type inference", TaskType.TYPE_INFERENCE),
    ("annotation", TaskType.TYPE_INFERENCE),
    ("dispatch", TaskType.DICT_DISPATCH),
    ("if/elif", TaskType.DICT_DISPATCH),
    ("dictionary", TaskType.DICT_DISPATCH),
    ("extract method", TaskType.EXTRACT_METHOD),
    ("helper", TaskType.EXTRACT_METHOD),
    ("repeated block", TaskType.EXTRACT_METHOD),
    ("error handling", TaskType.ERROR_HANDLING),
    ("try/except", TaskType.ERROR_HANDLING),
    ("exception", TaskType.ERROR_HANDLING),
    ("split", TaskType.SPLIT_FUNCTION),
    ("god function", TaskType.SPLIT_FUNCTION),
    ("too large", TaskType.SPLIT_FUNCTION),
    ("dependency cycle", TaskType.DEPENDENCY_CYCLE),
    ("circular dependency", TaskType.DEPENDENCY_CYCLE),
    ("api redesign", TaskType.API_REDESIGN),
    ("redesign", TaskType.API_REDESIGN),
]


def _classify_message(message: str) -> TaskType:
    """Classify a TODO message using pattern dispatch.

    CC: 4 (1 loop + 3 branches in fallback)
    Was: CC ~48 (25+ if/elif branches)
    """
    lowered = message.lower()

    for pattern, task_type in _CLASSIFY_PATTERNS:
        if pattern in lowered:
            return task_type

    # Fallback: magic number detection via "constant" keyword
    if "constant" in lowered and _first_int(message) is not None:
        return TaskType.KNOWN_MAGIC

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
