"""OpenRouter backend for AutoFix — direct API calls without proxy."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

from algitex.tools.autofix.base import FixResult, Task


class OpenRouterBackend:
    """Fix issues using OpenRouter API directly."""

    DEFAULT_TIMEOUT = 120
    DEFAULT_MAX_TOKENS = 2000
    API_BASE = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, dry_run: bool = False):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.model = model or os.environ.get("OPENROUTER_MODEL", "openrouter/qwen/qwen3-coder-next")
        self.dry_run = dry_run

    def fix(self, task: Task) -> FixResult:
        """Fix a task using OpenRouter API."""
        start_time = time.time()

        validation_result = self._validate(task, start_time)
        if validation_result:
            return validation_result

        if self.dry_run:
            return self._dry_run_result(task, start_time)

        return self._execute_fix(task, start_time)

    def _validate(self, task: Task, start_time: float) -> Optional[FixResult]:
        """Validate prerequisites."""
        if not task.file_path:
            return self._error_result(task, start_time, "No file path specified")

        if requests is None:
            return self._error_result(task, start_time, "requests library not available")

        if not self.api_key:
            return self._error_result(task, start_time, "OPENROUTER_API_KEY not set")

        return None

    def _execute_fix(self, task: Task, start_time: float) -> FixResult:
        """Execute the fix via OpenRouter API."""
        try:
            file_content = self._read_file(task.file_path)
            prompt = self._build_prompt(task, file_content)
            response = self._call_api(prompt)

            if response is None:
                return self._error_result(task, start_time, "API call failed")

            fixed_code = self._extract_code(response)
            self._write_file(task.file_path, fixed_code)

            return self._success_result(task, start_time)

        except Exception as e:
            return self._error_result(task, start_time, str(e))

    def _read_file(self, file_path: str) -> str:
        """Read file content."""
        return Path(file_path).read_text()

    def _build_prompt(self, task: Task, file_content: str) -> str:
        """Build prompt for the API."""
        return f"""Fix this specific issue in the code.

File: {task.file_path}
Line: {task.line_number or 'unknown'}
Issue: {task.description}

Current code:
```python
{file_content}
```

Provide ONLY the fixed code for this specific issue. Do not explain changes. Return the complete fixed file content."""

    def _call_api(self, prompt: str) -> Optional[str]:
        """Call OpenRouter API directly."""
        if requests is None:
            return None

        response = requests.post(
            f"{self.API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://algitex.local",
                "X-Title": "Algitex AutoFix"
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert Python code reviewer. Fix issues precisely."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": self.DEFAULT_MAX_TOKENS
            },
            timeout=self.DEFAULT_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        return None

    def _extract_code(self, response: str) -> str:
        """Extract code from markdown response."""
        match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        if match:
            return match.group(1)
        return response

    def _write_file(self, file_path: str, content: str) -> None:
        """Write fixed content to file."""
        Path(file_path).write_text(content)

    def _success_result(self, task: Task, start_time: float) -> FixResult:
        """Build success result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=True,
            method="openrouter",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path
        )

    def _dry_run_result(self, task: Task, start_time: float) -> FixResult:
        """Build dry-run result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=True,
            method="openrouter",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path,
            error="[DRY RUN]"
        )

    def _error_result(self, task: Task, start_time: float, error: str) -> FixResult:
        """Build error result."""
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            method="openrouter",
            time_ms=(time.time() - start_time) * 1000,
            file_path=task.file_path,
            error=error
        )
