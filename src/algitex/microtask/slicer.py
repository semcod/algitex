"""Context slicing helpers for MicroTask prompts."""

from __future__ import annotations

import ast
from pathlib import Path

from algitex.microtask import MicroTask


class ContextSlicer:
    """Extract the smallest useful context for a micro task."""

    def __init__(self, project_path: str | Path = ".") -> None:
        self.project_path = Path(project_path)

    def slice(self, task: MicroTask) -> MicroTask:
        """Populate context fields on a task and return it."""
        path = self._resolve_path(task.file)
        if not path.exists():
            task.context = ""
            task.context_tokens = 0
            return task

        source = path.read_text(encoding="utf-8")
        snippet = ""
        start_line = task.line_start
        end_line = task.line_end

        if task.function_name:
            extracted = self._extract_function(source, task.function_name, task.class_name)
            if extracted is not None:
                snippet, start_line, end_line = extracted
                task.context_start = start_line
                task.context_end = end_line
        if not snippet:
            start_line, end_line = self._expand_window(source, task.line_start, task.line_end)
            snippet = self._extract_lines(source, start_line, end_line)
            task.context_start = start_line
            task.context_end = end_line

        task.context = snippet
        task.context_tokens = self._estimate_tokens(snippet)
        return task

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path
        candidate = self.project_path / path
        if candidate.exists():
            return candidate
        return path

    def _extract_function(
        self,
        source: str,
        function_name: str,
        class_name: str = "",
    ) -> tuple[str, int, int] | None:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None

        lines = source.splitlines()

        def node_bounds(node: ast.AST) -> tuple[int, int]:
            start = getattr(node, "lineno", 1)
            decorators = getattr(node, "decorator_list", []) or []
            for decorator in decorators:
                start = min(start, getattr(decorator, "lineno", start))
            end = getattr(node, "end_lineno", start)
            return start, end

        if class_name:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == function_name:
                            start, end = node_bounds(child)
                            return ("\n".join(lines[start - 1 : end]), start, end)
                    break

        matches: list[tuple[int, int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                start, end = node_bounds(node)
                matches.append((start, end, "\n".join(lines[start - 1 : end])))

        if not matches:
            return None

        start, end, snippet = min(matches, key=lambda item: (item[1] - item[0], item[0]))
        return snippet, start, end

    def _expand_window(self, source: str, line_start: int, line_end: int) -> tuple[int, int]:
        lines = source.splitlines()
        if not lines:
            return line_start, line_end
        start = max(1, line_start - 3)
        end = min(len(lines), line_end + 3)
        return start, end

    def _extract_lines(self, source: str, start_line: int, end_line: int) -> str:
        lines = source.splitlines()
        if not lines:
            return ""
        start = max(1, start_line)
        end = min(len(lines), end_line)
        if start > end:
            return ""
        return "\n".join(lines[start - 1 : end])

    def _estimate_tokens(self, text: str) -> int:
        if not text.strip():
            return 0
        return max(1, int(round(len(text.split()) / 0.75)))


__all__ = ["ContextSlicer"]
