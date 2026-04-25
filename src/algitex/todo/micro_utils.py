"""Utility functions for micro-LLM fixes."""

from __future__ import annotations

import ast
import re
from typing import Any

from algitex.tools.todo_parser import Task

# Constants for micro-LLM operations
MAX_CONTEXT_LINES = 5
MAX_MAGIC_TOKENS = 40
TIMEOUT_SHORT = 60.0
TIMEOUT_LONG = 90.0
MAX_REWRITE_TOKENS = 350


def find_import_insert_point(lines: list[str]) -> int:
    """Find the line after the last import statement."""
    last_import = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            last_import = index + 1
    return last_import


def extract_first_int(text: str) -> int | None:
    """Extract the first integer from text."""
    match = re.search(r"\b(\d+)\b", text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def normalise_model_name(model: str) -> str:
    """Convert a user-facing model string into an Ollama model name."""
    return model.split("/", 1)[1] if model.startswith("ollama/") else model


def strip_code_fences(text: str) -> str:
    """Remove markdown fences if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def sanitize_constant_name(text: str, number: int) -> str:
    """Return a safe constant name from the model output."""
    candidate = text.strip().splitlines()[0].strip()
    candidate = re.sub(r"[^A-Za-z0-9_]+", "_", candidate).strip("_")
    if re.fullmatch(r"[A-Z][A-Z0-9_]+", candidate or ""):
        return candidate
    return f"MAGIC_{number}"


def validate_python(source: str) -> bool:
    """Validate Python source syntax."""
    try:
        ast.parse(source)
        return True
    except SyntaxError:
        return False


def coerce_task(task: Any) -> Task:
    """Convert different task dataclasses into a `todo_parser.Task`."""
    if isinstance(task, Task):
        return task

    file_path = getattr(task, "file_path", None) or getattr(task, "file", None)
    line_number = getattr(task, "line_number", None) or getattr(task, "line", None)
    description = getattr(task, "description", None) or getattr(task, "message", None) or ""
    task_id = getattr(task, "id", None) or f"{file_path}:{line_number or 0}"
    status = getattr(task, "status", None) or "pending"

    return Task(
        id=str(task_id),
        description=str(description),
        file_path=str(file_path) if file_path else None,
        line_number=int(line_number) if line_number else None,
        status=status,
    )
