"""Ollama backend for AutoFix."""

from __future__ import annotations

import time
from typing import Optional

from algitex.tools.autofix.base import FixResult, Task
from algitex.tools.ollama import OllamaService


class OllamaBackend:
    """Fix issues using Ollama local models."""

    def __init__(self, service: OllamaService, model: Optional[str] = None):
        self.service = service
        self.model = model

    def fix(self, task: Task) -> FixResult:
        """Fix a task using Ollama."""
        start_time = time.time()

        if not task.file_path:
            return self._error_result(task, start_time, "No file path specified")

        try:
            model = self._ensure_model()
            if not model:
                return self._error_result(task, start_time, "No suitable model found")

            success = self._apply_fix(task, model)
            return self._success_result(task, start_time, success)

        except Exception as e:
            return self._error_result(task, start_time, str(e))

    def _ensure_model(self) -> Optional[str]:
        """Ensure we have a model to use."""
        if self.model:
            return self.model

        models = self.service.get_recommended_models()
        if models:
            self.model = models[0]
            return self.model
        return None

    def _apply_fix(self, task: Task, model: str) -> bool:
        """Apply the fix to the file."""
        return self.service.auto_fix_file(
            task.file_path,
            task.description,
            task.line_number,
            model
        )

    def _success_result(self, task: Task, start_time: float, success: bool) -> FixResult:
        """Build a success result."""
        elapsed = (time.time() - start_time) * 1000
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=success,
            method="ollama",
            time_ms=elapsed,
            file_path=task.file_path,
            error=None if success else "Failed to fix code"
        )

    def _error_result(self, task: Task, start_time: float, error: str) -> FixResult:
        """Build an error result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            method="ollama",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path,
            error=error
        )
