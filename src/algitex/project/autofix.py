"""AutoFix integration mixins for Project class."""

from __future__ import annotations

from typing import Optional

from algitex.tools.autofix import AutoFix


class AutoFixMixin:
    """AutoFix integration functionality for Project."""

    def __init__(self, todo_path: str) -> None:
        self.autofix = AutoFix(todo_path)

    def fix_issues(
        self,
        limit: Optional[int] = None,
        backend: str = "auto",
        filter_file: Optional[str] = None
    ) -> dict:
        """Fix issues from TODO.md."""
        results = self.autofix.fix_all(limit=limit, backend=backend, filter_file=filter_file)

        # Sync with tickets system if any fixes were made
        if any(r.success for r in results):
            self.sync()

        return {
            "total": len(results),
            "fixed": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [r.to_dict() for r in results]
        }

    def fix_issue(self, task_id: str, backend: str = "auto") -> Optional[dict]:
        """Fix a specific issue by task ID."""
        result = self.autofix.fix_issue(task_id, backend)
        if result and result.success:
            self.sync()
            return result.to_dict()
        return None

    def list_todo_tasks(self) -> list:
        """List all pending TODO tasks."""
        tasks = self.autofix.list_tasks()
        return [t.to_dict() for t in tasks]

    def sync(self) -> dict:
        """Sync tickets to external backend."""
        from algitex.tools.tickets import Tickets
        return Tickets().sync()
