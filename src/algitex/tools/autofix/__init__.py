"""AutoFix — automated code fixing from TODO items.

Refactored: split into backend-specific modules to reduce complexity.

Usage:
    from algitex.tools.autofix import AutoFix

    autofix = AutoFix()
    autofix.fix_all(limit=5)
    autofix.fix_issue("TASK-001")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from algitex.tools.autofix.base import FixResult, Task
from algitex.tools.autofix.ollama_backend import OllamaBackend
from algitex.tools.autofix.aider_backend import AiderBackend
from algitex.tools.autofix.proxy_backend import ProxyBackend
from algitex.tools.todo_parser import TodoParser
from algitex.tools.ollama import OllamaClient, OllamaService
from algitex.tools.services import ServiceChecker


class AutoFix:
    """Automated code fixing using various backends."""

    def __init__(
        self,
        todo_file: str = "TODO.md",
        backend: str = "auto",  # "auto", "ollama", "aider", "litellm-proxy"
        ollama_model: Optional[str] = None,
        proxy_url: str = "http://localhost:4000",
        dry_run: bool = False
    ):
        self.todo_file = Path(todo_file)
        self.backend = backend
        self.ollama_model = ollama_model
        self.proxy_url = proxy_url
        self.dry_run = dry_run

        # Initialize components
        self.parser = TodoParser(str(self.todo_file))
        self.service_checker = ServiceChecker()

        # Lazy initialization of backends
        self._ollama_service: Optional[OllamaService] = None
        self._ollama_backend: Optional[OllamaBackend] = None
        self._aider_backend: Optional[AiderBackend] = None
        self._proxy_backend: Optional[ProxyBackend] = None

    @property
    def ollama_service(self) -> OllamaService:
        """Get Ollama service instance."""
        if self._ollama_service is None:
            client = OllamaClient(default_model=self.ollama_model)
            self._ollama_service = OllamaService(client)
        return self._ollama_service

    @property
    def ollama_backend(self) -> OllamaBackend:
        """Get Ollama backend instance."""
        if self._ollama_backend is None:
            self._ollama_backend = OllamaBackend(self.ollama_service, self.ollama_model)
        return self._ollama_backend

    @property
    def aider_backend(self) -> AiderBackend:
        """Get Aider backend instance."""
        if self._aider_backend is None:
            self._aider_backend = AiderBackend(dry_run=self.dry_run)
        return self._aider_backend

    @property
    def proxy_backend(self) -> ProxyBackend:
        """Get Proxy backend instance."""
        if self._proxy_backend is None:
            self._proxy_backend = ProxyBackend(self.proxy_url, dry_run=self.dry_run)
        return self._proxy_backend

    def check_backends(self) -> Dict[str, bool]:
        """Check which backends are available."""
        available = {}

        # Check Ollama
        ollama_status = self.service_checker.check_ollama()
        available["ollama"] = ollama_status.healthy

        # Check Aider
        aider_status = self.service_checker.check_command_exists("aider", "aider")
        available["aider"] = aider_status.healthy

        # Check LiteLLM proxy
        proxy_status = self.service_checker.check_litellm_proxy(self.proxy_url)
        available["litellm-proxy"] = proxy_status.healthy

        return available

    def choose_backend(self) -> str:
        """Choose the best available backend."""
        if self.backend != "auto":
            return self.backend

        available = self.check_backends()

        # Priority: Ollama > LiteLLM proxy > Aider
        if available.get("ollama"):
            return "ollama"
        elif available.get("litellm-proxy"):
            return "litellm-proxy"
        elif available.get("aider"):
            return "aider"
        else:
            raise RuntimeError("No fixing backend available")

    def _convert_task(self, task: Any) -> Task:
        """Convert todo_parser.Task to autofix.Task."""
        return Task(
            id=task.id,
            description=task.description,
            file_path=task.file_path,
            line_number=task.line_number,
            status=task.status,
            priority=task.priority,
            type=task.type
        )

    def mark_task_done(self, task: Any) -> bool:
        """Mark a task as done in TODO.md."""
        try:
            content = self.todo_file.read_text(encoding='utf-8')

            # Find and replace the task line
            if task.file_path and task.line_number:
                # Prefact format: file.py:line - description
                search_line = f"- [ ] {task.file_path}:{task.line_number} - {task.description}"
                replace_line = f"- [x] {task.file_path}:{task.line_number} - {task.description}"
            else:
                # Generic format
                search_line = f"- [ ] {task.description}"
                replace_line = f"- [x] {task.description}"

            if search_line in content:
                content = content.replace(search_line, replace_line, 1)
                self.todo_file.write_text(content, encoding='utf-8')
                return True

            # Try more flexible matching
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if task.description in line and "- [ ]" in line:
                    lines[i] = line.replace("- [ ]", "- [x]", 1)
                    self.todo_file.write_text('\n'.join(lines), encoding='utf-8')
                    return True

            return False
        except Exception as e:
            print(f"Warning: Could not mark task as done: {e}")
            return False

    def fix_with_ollama(self, task: Any) -> FixResult:
        """Fix using Ollama."""
        converted = self._convert_task(task)
        return self.ollama_backend.fix(converted)

    def fix_with_aider(self, task: Any) -> FixResult:
        """Fix using Aider CLI."""
        converted = self._convert_task(task)
        return self.aider_backend.fix(converted)

    def fix_with_proxy(self, task: Any) -> FixResult:
        """Fix using LiteLLM proxy."""
        converted = self._convert_task(task)
        return self.proxy_backend.fix(converted)

    def fix_task(self, task: Any, backend: Optional[str] = None) -> FixResult:
        """Fix a single task."""
        backend = backend or self.choose_backend()

        if backend == "ollama":
            return self.fix_with_ollama(task)
        elif backend == "aider":
            return self.fix_with_aider(task)
        elif backend == "litellm-proxy":
            return self.fix_with_proxy(task)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def fix_all(
        self,
        limit: Optional[int] = None,
        backend: Optional[str] = None,
        filter_file: Optional[str] = None
    ) -> List[FixResult]:
        """Fix all pending tasks."""
        # Parse tasks
        tasks = self.parser.parse()

        # Apply filters
        if filter_file:
            tasks = [t for t in tasks if t.file_path == filter_file]

        if limit:
            tasks = tasks[:limit]

        if not tasks:
            print("No tasks found to fix.")
            return []

        # Choose backend
        backend = backend or self.choose_backend()
        print(f"Using backend: {backend}")

        # Fix tasks
        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] Fixing {task.id}: {task.description[:50]}...")

            result = self.fix_task(task, backend)
            results.append(result)

            if result.success:
                print(f"   ✅ Fixed with {result.method} ({result.time_ms:.0f}ms)")
                if not self.dry_run:
                    if self.mark_task_done(task):
                        print(f"   ✅ Marked as done in TODO.md")
            else:
                print(f"   ❌ Failed: {result.error}")

        # Print summary
        self.print_summary(results)

        return results

    def fix_issue(self, task_id: str, backend: Optional[str] = None) -> Optional[FixResult]:
        """Fix a specific task by ID."""
        tasks = self.parser.parse()
        task = next((t for t in tasks if t.id == task_id), None)

        if not task:
            print(f"Task {task_id} not found")
            return None

        print(f"Fixing {task_id}: {task.description}")

        result = self.fix_task(task, backend)

        if result.success:
            print(f"✅ Fixed with {result.method}")
            if not self.dry_run:
                self.mark_task_done(task)
        else:
            print(f"❌ Failed: {result.error}")

        return result

    def print_summary(self, results: List[FixResult]):
        """Print summary of fixing results."""
        print("\n" + "=" * 70)
        print("AutoFix Summary")
        print("=" * 70)

        total = len(results)
        fixed = sum(1 for r in results if r.success)
        failed = total - fixed

        print(f"Total issues: {total}")
        print(f"✅ Fixed: {fixed}")
        print(f"❌ Failed: {failed}")

        if failed > 0:
            print("\nFailed issues:")
            for r in results:
                if not r.success:
                    print(f"  - {r.task_id}: {r.error}")

        # Group by method
        by_method = {}
        for r in results:
            if r.success:
                by_method.setdefault(r.method, 0)
                by_method[r.method] += 1

        if by_method:
            print("\nFixed by method:")
            for method, count in by_method.items():
                print(f"  - {method}: {count}")

        if not self.dry_run and fixed > 0:
            print(f"\n📝 Review changes with: git diff")
            print(f"🚀 Commit with: git commit -m 'Fix {fixed} issues via AutoFix'")

    def list_tasks(self) -> List[Any]:
        """List all pending tasks."""
        return self.parser.parse()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tasks."""
        return self.parser.get_stats()


# Backward compatibility exports
__all__ = ["AutoFix", "FixResult", "Task"]
