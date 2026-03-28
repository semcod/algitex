"""Ollama backend for AutoFix."""

from __future__ import annotations

import time
from typing import Optional

from algitex.tools.autofix.base import FixResult, Task
from algitex.tools.ollama import OllamaService, OllamaClient


class OllamaBackend:
    """Fix issues using Ollama local models."""

    DEFAULT_TIMEOUT = 30.0  # seconds

    def __init__(
        self,
        service: Optional[OllamaService] = None,
        model: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        dry_run: bool = True,
        timeout: float = DEFAULT_TIMEOUT
    ):
        if service:
            self.service = service
        else:
            client = OllamaClient(host=base_url, timeout=timeout)
            self.service = OllamaService(client=client)
        self.model = model
        self.base_url = base_url
        self.dry_run = dry_run
        self.timeout = timeout

    def fix(self, task: Task) -> FixResult:
        """Fix a task using Ollama."""
        start_time = time.time()

        if not task.file_path:
            return self._error_result(task, start_time, "No file path specified")

        # Quick health check
        if not self._is_healthy():
            return self._error_result(task, start_time, "Ollama not available at " + self.base_url)

        try:
            model = self._ensure_model()
            if not model:
                return self._error_result(task, start_time, "No suitable model found")

            if self.dry_run:
                return self._success_result(task, start_time, True, method="ollama-dry-run")

            success = self._apply_fix(task, model)
            return self._success_result(task, start_time, success, method="ollama")

        except Exception as e:
            return self._error_result(task, start_time, str(e))

    def _is_healthy(self) -> bool:
        """Quick health check to avoid hanging."""
        try:
            import socket
            host = self.base_url.replace("http://", "").replace("https://", "").split(":")[0]
            port = 11434
            if ":" in self.base_url.replace("http://", "").replace("https://", ""):
                port_str = self.base_url.replace("http://", "").replace("https://", "").split(":")[1]
                port = int(port_str.split("/")[0])
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

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

    def _success_result(self, task: Task, start_time: float, success: bool, method: str = "ollama") -> FixResult:
        """Create a success result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=success,
            method=method,
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path
        )

    def _error_result(self, task: Task, start_time: float, error: str) -> FixResult:
        """Create an error result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            method="ollama",
            time_ms=(time.time() - start_time) * 1000,
            error=error,
            file_path=task.file_path
        )
