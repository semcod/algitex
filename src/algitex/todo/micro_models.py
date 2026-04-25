"""Data models for micro-LLM fixes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FunctionSnippet:
    """Minimal source slice around a function or method."""

    file_path: str
    name: str
    kind: str
    start_line: int
    end_line: int
    source: str

    @property
    def line_count(self) -> int:
        """Return the number of lines in the snippet."""
        return max(0, self.end_line - self.start_line + 1)


@dataclass
class MicroFixResult:
    """Result of a micro-LLM fix."""

    task_id: str
    task_description: str
    category: str
    tier: str = "micro"
    success: bool = False
    method: str = "micro-llm"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    error: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)
