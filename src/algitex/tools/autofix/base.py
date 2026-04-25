"""Base classes and utilities for AutoFix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from algitex.tools.todo_parser import Task


@dataclass
class FixResult:
    """Result of fixing an issue."""
    task_id: str
    task_description: str = ""
    success: bool = False
    method: str = ""  # "ollama", "aider", "litellm-proxy"
    time_ms: Optional[float] = None
    error: Optional[str] = None
    file_path: Optional[str] = None
    diff: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "success": self.success,
            "method": self.method,
            "time_ms": self.time_ms,
            "error": self.error,
            "file_path": self.file_path
        }


class AutoFixBackend:
    """Base class for autofix backends."""
    
    def fix(self, task: Task) -> FixResult:
        """Fix a task. Override in subclass."""
        raise NotImplementedError("Subclasses must implement fix()")
    status: str = "pending"
    priority: str = "normal"
    type: str = "task"
