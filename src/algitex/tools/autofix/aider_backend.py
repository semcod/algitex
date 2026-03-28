"""Aider backend for AutoFix — refactored to reduce cyclomatic complexity."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import List, Optional

from algitex.tools.autofix.base import FixResult, Task


class AiderBackend:
    """Fix issues using Aider CLI."""

    DEFAULT_TIMEOUT = 300  # 5 minutes
    DEFAULT_MODEL = "ollama/qwen3-coder:latest"

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def fix(self, task: Task) -> FixResult:
        """Fix a task using Aider — main entry point with reduced CC."""
        start_time = time.time()

        validation_result = self._validate_task(task, start_time)
        if validation_result:
            return validation_result

        self._ensure_git_repo()

        if self.dry_run:
            return self._dry_run_result(task, start_time)

        return self._execute_aider(task, start_time)

    def _validate_task(self, task: Task, start_time: float) -> Optional[FixResult]:
        """Validate task has required fields."""
        if not task.file_path:
            return self._error_result(task, start_time, "No file path specified")
        return None

    def _ensure_git_repo(self) -> None:
        """Ensure git repository exists for aider."""
        if Path(".git").exists():
            return

        subprocess.run(["git", "init"], capture_output=True, check=False)
        subprocess.run(
            ["git", "config", "user.email", "autofix@local"],
            capture_output=True, check=False
        )
        subprocess.run(
            ["git", "config", "user.name", "AutoFix"],
            capture_output=True, check=False
        )

    def _build_command(self, task: Task) -> List[str]:
        """Build the aider command with all arguments."""
        prompt = self._build_prompt(task)

        return [
            "aider",
            "--model", self.DEFAULT_MODEL,
            "--no-git",
            "--no-commit",
            "--yes",
            "--no-check-version",
            "--message", prompt,
            task.file_path
        ]

    def _build_prompt(self, task: Task) -> str:
        """Build the prompt for aider."""
        parts = [f"Fix this issue in {task.file_path}"]
        if task.line_number:
            parts.append(f" at line {task.line_number}")
        parts.append(f":\n{task.description}\n\n")
        parts.append("Make minimal changes to fix only this specific issue.")
        return "".join(parts)

    def _execute_aider(self, task: Task, start_time: float) -> FixResult:
        """Execute aider subprocess and handle results."""
        cmd = self._build_command(task)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.DEFAULT_TIMEOUT
            )
            return self._process_result(task, start_time, result)

        except subprocess.TimeoutExpired:
            return self._timeout_result(task, start_time)
        except Exception as e:
            return self._error_result(task, start_time, str(e))

    def _process_result(
        self,
        task: Task,
        start_time: float,
        result: subprocess.CompletedProcess
    ) -> FixResult:
        """Process subprocess result into FixResult."""
        elapsed = (time.time() - start_time) * 1000

        if result.returncode == 0:
            return FixResult(
                task_id=task.id,
                task_description=task.description,
                success=True,
                method="aider",
                time_ms=elapsed,
                file_path=task.file_path
            )

        error_msg = result.stderr[:200] if result.stderr else "Aider failed"
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            method="aider",
            time_ms=elapsed,
            file_path=task.file_path,
            error=error_msg
        )

    def _dry_run_result(self, task: Task, start_time: float) -> FixResult:
        """Return dry-run result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=True,
            method="aider",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path,
            error="[DRY RUN]"
        )

    def _timeout_result(self, task: Task, start_time: float) -> FixResult:
        """Return timeout error result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            method="aider",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path,
            error=f"Timeout ({self.DEFAULT_TIMEOUT // 60}min)"
        )

    def _error_result(self, task: Task, start_time: float, error: str) -> FixResult:
        """Return generic error result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            method="aider",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path,
            error=error
        )
