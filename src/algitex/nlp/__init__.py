"""Deterministic NLP refactor helpers for algitex."""

from __future__ import annotations

import ast
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

IGNORED_PARTS = {
    ".git",
    ".algitex",
    "__pycache__",
    ".pytest_cache",
    "htmlcov",
    "node_modules",
    "venv",
    ".venv",
}


@dataclass
class DocstringChange:
    """Single docstring rewrite."""

    file: str
    line: int
    before: str
    after: str
    node_type: str


class DocstringShortener:
    """Shorten verbose docstrings to one or two lines."""

    def shorten(self, docstring: str) -> str | None:
        """Return a shorter version of a docstring or None if unchanged."""
        text = re.sub(r"\s+", " ", docstring.strip())
        if not text:
            return None

        summary = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9`\"'])", text, maxsplit=1)[0].strip()
        if len(summary) > 120:
            summary = summary[:117].rstrip() + "..."

        if summary == text and len(text) <= 120:
            return None
        return summary

    def fix_file(self, path: str | Path, apply: bool = True) -> list[dict[str, object]]:
        """Shorten docstrings in a single Python file."""
        file_path = Path(path)
        if not file_path.exists() or file_path.suffix != ".py":
            return []

        source = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        lines = source.splitlines()
        changes: list[dict[str, object]] = []
        replacements: list[tuple[int, int, list[str], dict[str, object]]] = []

        for node, expr, docstring in self._iter_docstring_nodes(tree):
            shorter = self.shorten(docstring)
            if shorter is None:
                continue
            start = expr.lineno - 1
            end = getattr(expr, "end_lineno", expr.lineno) - 1
            indent = re.match(r"\s*", lines[start]).group(0) if start < len(lines) else ""
            rendered = f'{indent}"""{shorter.replace("\"\"\"", "\\\"\\\"\\\"")}"""'
            before = "\n".join(lines[start : end + 1])
            change = {
                "file": str(file_path),
                "line": expr.lineno,
                "before": before,
                "after": rendered,
                "node_type": type(node).__name__,
            }
            changes.append(change)
            replacements.append((start, end, rendered.splitlines(), change))

        if apply and replacements:
            working = lines[:]
            for start, end, replacement, _ in sorted(replacements, key=lambda item: item[0], reverse=True):
                working[start : end + 1] = replacement
            new_source = "\n".join(working)
            if source.endswith("\n"):
                new_source += "\n"
            file_path.write_text(new_source, encoding="utf-8")

        return changes

    def fix_path(self, path: str | Path, apply: bool = True) -> list[dict[str, object]]:
        """Shorten docstrings in a file or directory tree."""
        target = Path(path)
        files = [target] if target.is_file() else list(_python_files(target))
        changes: list[dict[str, object]] = []
        for file_path in files:
            changes.extend(self.fix_file(file_path, apply=apply))
        return changes

    def _iter_docstring_nodes(self, tree: ast.AST):
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if not body:
                continue
            expr = body[0]
            if not isinstance(expr, ast.Expr):
                continue
            value = getattr(expr, "value", None)
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                yield node, expr, value.value
            elif isinstance(value, ast.Str):
                yield node, expr, value.s


class DeadCodeDetector:
    """Detect top-level functions that appear unused."""

    def scan(self, project_path: str | Path) -> list[dict[str, object]]:
        """Return a list of dead top-level functions."""
        root = Path(project_path)
        results: list[dict[str, object]] = []
        for file_path in _python_files(root):
            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                continue

            collector = _UsageCollector()
            collector.visit(tree)

            for name, line in collector.defined:
                if name.startswith("_"):
                    continue
                if name not in collector.references:
                    results.append(
                        {
                            "name": name,
                            "file": str(file_path),
                            "line": line,
                            "reason": "defined but never referenced",
                        }
                    )
        results.sort(key=lambda item: (item["file"], item["line"], item["name"]))
        return results


@dataclass
class _DuplicateWindow:
    file: str
    line: int
    text: tuple[str, ...]


class _UsageCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.depth = 0
        self.defined: list[tuple[str, int]] = []
        self.references: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.depth == 0 and not node.name.startswith("_"):
            self.defined.append((node.name, node.lineno))
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_Name(self, node: ast.Name) -> None:
        self.references.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.references.add(node.attr)
        self.generic_visit(node)


def sort_imports_in_path(path: str | Path, apply: bool = True) -> dict[str, int]:
    """Sort imports in a file or directory tree, preferring isort when available."""
    target = Path(path)
    files = [target] if target.is_file() else list(_python_files(target))
    changed = 0
    errors = 0

    for file_path in files:
        try:
            original = file_path.read_text(encoding="utf-8")
            sorted_source = _sort_imports(original)
            if sorted_source != original:
                changed += 1
                if apply:
                    file_path.write_text(sorted_source, encoding="utf-8")
        except Exception:
            errors += 1

    return {"files": len(files), "changed": changed, "errors": errors}


def find_duplicate_blocks(project_path: str | Path, min_lines: int = 3) -> list[dict[str, object]]:
    """Find repeated code blocks with a rolling hash over line windows."""
    if min_lines < 2:
        min_lines = 2

    groups: dict[int, list[_DuplicateWindow]] = defaultdict(list)
    for file_path in _python_files(Path(project_path)):
        try:
            lines = [line.rstrip() for line in file_path.read_text(encoding="utf-8").splitlines()]
        except OSError:
            continue
        if len(lines) < min_lines:
            continue

        line_hashes = [_stable_line_hash(line) for line in lines]
        base = 257
        mod = 2**61 - 1
        power = pow(base, min_lines - 1, mod)
        window_hash = 0

        for index, line_hash in enumerate(line_hashes):
            window_hash = (window_hash * base + line_hash) % mod
            if index >= min_lines:
                window_hash = (window_hash - line_hashes[index - min_lines] * power) % mod
            if index + 1 >= min_lines:
                start = index - min_lines + 1
                block = tuple(lines[start : start + min_lines])
                groups[window_hash].append(_DuplicateWindow(file=str(file_path), line=start + 1, text=block))

    results: list[dict[str, object]] = []
    for fingerprint, windows in groups.items():
        by_text: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
        for window in windows:
            by_text[window.text].append({"file": window.file, "line": window.line})
        for text, occurrences in by_text.items():
            if len(occurrences) < 2:
                continue
            results.append(
                {
                    "hash": str(fingerprint),
                    "lines": min_lines,
                    "text": "\n".join(text),
                    "occurrences": occurrences,
                }
            )

    results.sort(key=lambda item: (-len(item["occurrences"]), item["occurrences"][0]["file"], item["occurrences"][0]["line"]))
    return results


def _sort_imports(source: str) -> str:
    try:
        from isort import code as isort_code
    except ImportError:
        return _fallback_sort_imports(source)

    try:
        sorted_source = isort_code(source, profile="black")
    except Exception:
        return _fallback_sort_imports(source)
    return _ensure_trailing_newline(sorted_source)


def _fallback_sort_imports(source: str) -> str:
    lines = source.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        if stripped.startswith(("import ", "from ")):
            block = [line]
            index += 1
            while index < len(lines):
                next_line = lines[index]
                next_stripped = next_line.lstrip()
                if not next_line.strip():
                    break
                if next_stripped.startswith(("import ", "from ")):
                    block.append(next_line)
                    index += 1
                    continue
                break
            output.extend(sorted(block, key=lambda item: item.strip().lower()))
            continue

        output.append(line)
        index += 1

    return _ensure_trailing_newline("\n".join(output))


def _python_files(path: Path):
    if not path.exists():
        return []
    if path.is_file():
        return [path] if path.suffix == ".py" else []
    return [file_path for file_path in path.rglob("*.py") if not _is_ignored(file_path)]


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def _ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def _stable_line_hash(line: str) -> int:
    return int.from_bytes(hashlib.blake2b(line.encode("utf-8"), digest_size=8).digest(), "big")


__all__ = [
    "DeadCodeDetector",
    "DocstringChange",
    "DocstringShortener",
    "find_duplicate_blocks",
    "sort_imports_in_path",
]
