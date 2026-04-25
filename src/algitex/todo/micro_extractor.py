"""Extract code snippets around TODO task lines."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Optional

from algitex.todo.micro_models import FunctionSnippet
from algitex.todo.micro_utils import MAX_CONTEXT_LINES


class FunctionExtractor:
    """Extract a single function or method around a task line."""

    def extract(self, path: Path, line_number: Optional[int]) -> FunctionSnippet | None:
        """Return the innermost function/method containing the requested line."""
        if not line_number or not path.exists() or path.suffix != ".py":
            return None

        source = path.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None

        lines = source.splitlines()
        candidates: list[ast.AST] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            end_line = getattr(node, "end_lineno", None)
            if end_line is None:
                continue
            if node.lineno <= line_number <= end_line:
                candidates.append(node)

        if not candidates:
            start = max(1, line_number - MAX_CONTEXT_LINES)
            end = min(len(lines), line_number + MAX_CONTEXT_LINES)
            snippet_source = "\n".join(lines[start - 1 : end])
            return FunctionSnippet(
                file_path=str(path),
                name="<module>",
                kind="module",
                start_line=start,
                end_line=end,
                source=snippet_source,
            )

        node = min(
            candidates,
            key=lambda item: (getattr(item, "end_lineno", item.lineno) - item.lineno, item.lineno),
        )
        end_line = getattr(node, "end_lineno", node.lineno)
        snippet_source = "\n".join(lines[node.lineno - 1 : end_line])
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        return FunctionSnippet(
            file_path=str(path),
            name=getattr(node, "name", "<unknown>"),
            kind=kind,
            start_line=node.lineno,
            end_line=end_line,
            source=snippet_source,
        )
