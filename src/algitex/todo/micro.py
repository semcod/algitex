"""Micro-LLM fixes for TODO tasks.

This module extracts the smallest useful code snippet around a TODO task,
feeds it to a local Ollama model, and applies the returned micro-fix back to
source code. It is intentionally conservative: only tasks that map to a single
function or a simple constant-name rewrite are handled here.
"""

from __future__ import annotations

import ast
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from algitex.tools.ollama import OllamaClient
from algitex.tools.todo_parser import TodoParser, Task
from algitex.todo.tiering import TaskTriage, classify_task


@dataclass
class FunctionSnippet:
    """Minimal source slice around a function or method."""

    file_path: str
    name: str
    kind: str
    start_line: int
    end_line: int
    source: str

    @property
    def line_count(self) -> int:
        """Return the number of lines in the snippet."""
        return max(0, self.end_line - self.start_line + 1)


@dataclass
class MicroFixResult:
    """Result of a micro-LLM fix."""

    task_id: str
    task_description: str
    category: str
    tier: str = "micro"
    success: bool = False
    method: str = "micro-llm"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    error: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)


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
            return None

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


class MicroPromptBuilder:
    """Build narrow prompts for micro-LLM fixes."""

    SYSTEM_PROMPT = (
        "You are a precise Python refactoring assistant. "
        "Make the smallest possible change. Return ONLY the requested content."
    )

    def build(self, triage: TaskTriage, snippet: FunctionSnippet, task: Task) -> list[dict[str, str]]:
        """Build Ollama chat messages for the given task."""
        prompt = self._build_user_prompt(triage, snippet, task)
        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

    def _build_user_prompt(self, triage: TaskTriage, snippet: FunctionSnippet, task: Task) -> str:
        """Create the user-facing prompt text."""
        header = [
            f"Task category: {triage.category}",
            f"File: {task.file_path or snippet.file_path}",
            f"Line: {task.line_number or snippet.start_line}",
            f"Target: {snippet.kind} `{snippet.name}`",
            "",
        ]

        if triage.category == "docstring":
            instruction = (
                "Rewrite the function docstring to be concise (1-2 lines max). "
                "Preserve behavior and public API. Return ONLY the updated function source."
            )
        elif triage.category == "rename":
            instruction = (
                "Rename the unclear variable(s) to more descriptive names within this function. "
                "Make the smallest safe edit and return ONLY the updated function source."
            )
        elif triage.category == "guard_clause":
            instruction = (
                "Add one guard clause for the indicated parameter or input validation path. "
                "Do not refactor unrelated code. Return ONLY the updated function source."
            )
        elif triage.category == "dispatch":
            instruction = (
                "If appropriate, convert the branching logic to a small dictionary dispatch or lookup table. "
                "Keep the behavior identical. Return ONLY the updated function source."
            )
        elif triage.category == "magic":
            number = triage.number if triage.number is not None else _extract_first_int(task.description)
            instruction = (
                f"Suggest a descriptive UPPER_SNAKE_CASE constant name for the magic number {number}. "
                "Return ONLY the name, nothing else."
            )
        else:
            instruction = (
                "Improve this function with a minimal local edit that matches the task. "
                "Return ONLY the updated function source."
            )

        return "\n".join(header + [instruction, "", "```python", snippet.source, "```"])


class MicroFixer:
    """Execute micro-LLM fixes on a TODO file."""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:7b",
        workers: int = 4,
        dry_run: bool = True,
    ):
        self.ollama_url = ollama_url
        self.model = _normalise_model_name(model)
        self.workers = workers
        self.dry_run = dry_run
        self.extractor = FunctionExtractor()
        self.prompt_builder = MicroPromptBuilder()

    def fix_file(self, file_path: Path, tasks: list[Task]) -> list[MicroFixResult]:
        """Fix all micro-LLM tasks in a single file."""
        path = Path(file_path)
        if not path.exists():
            return [
                MicroFixResult(
                    task_id=task.id,
                    task_description=task.description,
                    category=classify_task(task).category,
                    success=False,
                    file_path=str(path),
                    line_number=task.line_number,
                    error="file not found",
                )
                for task in tasks
            ]

        results: list[MicroFixResult] = []
        for task in sorted((_coerce_task(item) for item in tasks), key=lambda item: item.line_number or 0, reverse=True):
            results.append(self.fix_task(task))
        return results

    def fix_task(self, task: Task) -> MicroFixResult:
        """Fix a single micro task."""
        task = _coerce_task(task)
        triage = classify_task(task)
        path = Path(task.file_path) if task.file_path else None
        if not path:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                error="no file path",
            )

        if self.dry_run:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=True,
                method="micro-dry-run",
                file_path=str(path),
                line_number=task.line_number,
                details={"tier": triage.tier, "reason": triage.reason},
            )

        if triage.category == "magic":
            return self._fix_magic_name(task, triage, path)

        snippet = self.extractor.extract(path, task.line_number)
        if not snippet:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="no function snippet found",
            )

        client = OllamaClient(host=self.ollama_url, default_model=self.model, timeout=90.0)
        try:
            messages = self.prompt_builder.build(triage, snippet, task)
            response = client.chat(messages=messages, model=self.model, temperature=0.0, max_tokens=350)
            content = _strip_code_fences(response.content)
            if not content.strip():
                return MicroFixResult(
                    task_id=task.id,
                    task_description=task.description,
                    category=triage.category,
                    success=False,
                    file_path=str(path),
                    line_number=task.line_number,
                    error="empty ollama response",
                )

            return self._apply_function_rewrite(task, triage, path, snippet, content)
        except Exception as exc:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error=str(exc),
            )
        finally:
            client.close()

    def run(
        self,
        todo_path: str | Path = "TODO.md",
        limit: int = 0,
        categories: set[str] | None = None,
    ) -> dict[str, int]:
        """Run all micro tasks from a TODO file."""
        tasks = TodoParser(todo_path).parse()
        if limit > 0:
            tasks = tasks[:limit]

        return self.fix_tasks(tasks, categories=categories)

    def fix_tasks(self, tasks: list[Task], categories: set[str] | None = None) -> dict[str, int]:
        """Run micro fixes on an already-parsed task list."""
        micro_tasks = [_coerce_task(task) for task in tasks if classify_task(task).tier == "micro"]
        if categories:
            micro_tasks = [task for task in micro_tasks if classify_task(task).category in categories]

        if not micro_tasks:
            print("No micro-LLM tasks found.")
            return {"fixed": 0, "skipped": 0, "errors": 0}

        by_file_map: dict[str, list[Task]] = {}
        for task in micro_tasks:
            if not task.file_path:
                continue
            by_file_map.setdefault(task.file_path, []).append(task)

        fixed = 0
        skipped = 0
        errors = 0
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {
                pool.submit(self.fix_file, Path(file_path), file_tasks): file_path
                for file_path, file_tasks in by_file_map.items()
            }
            for future in as_completed(futures):
                try:
                    results = future.result()
                    fixed += sum(1 for item in results if item.success)
                    skipped += sum(1 for item in results if not item.success and not item.error)
                    errors += sum(1 for item in results if item.error)
                except Exception as exc:
                    errors += 1
                    print(f"  ✗ Micro fix failed: {exc}")

        print(f"Micro LLM: fixed={fixed}, skipped={skipped}, errors={errors}")
        return {"fixed": fixed, "skipped": skipped, "errors": errors}

    def _fix_magic_name(self, task: Task, triage: TaskTriage, path: Path) -> MicroFixResult:
        """Ask the model for a constant name and apply it."""
        number = triage.number if triage.number is not None else _extract_first_int(task.description)
        if number is None:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="could not determine magic number",
            )

        snippet = self.extractor.extract(path, task.line_number)
        if not snippet:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="no function snippet found",
            )

        client = OllamaClient(host=self.ollama_url, default_model=self.model, timeout=60.0)
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a precise Python refactoring assistant. Return only a constant name in UPPER_SNAKE_CASE.",
                },
                {
                    "role": "user",
                    "content": "\n".join(
                        [
                            f"Suggest a descriptive constant name for the magic number {number}.",
                            f"File: {task.file_path}",
                            f"Line: {task.line_number}",
                            "",
                            "```python",
                            snippet.source,
                            "```",
                        ]
                    ),
                },
            ]
            response = client.chat(messages=messages, model=self.model, temperature=0.0, max_tokens=40)
            const_name = _sanitize_constant_name(response.content, number)
            return self._apply_magic_name(task, triage, path, number, const_name)
        except Exception as exc:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error=str(exc),
            )
        finally:
            client.close()

    def _apply_function_rewrite(
        self,
        task: Task,
        triage: TaskTriage,
        path: Path,
        snippet: FunctionSnippet,
        new_source: str,
    ) -> MicroFixResult:
        """Replace a function snippet and validate the resulting file."""
        original_text = path.read_text()
        lines = original_text.splitlines()
        replacement = new_source.strip()
        if not replacement:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="empty rewrite",
            )

        new_lines = replacement.splitlines()
        lines[snippet.start_line - 1 : snippet.end_line] = new_lines
        candidate = "\n".join(lines) + "\n"
        if not _validate_python(candidate):
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="rewrite produced invalid python",
            )

        path.write_text(candidate)
        return MicroFixResult(
            task_id=task.id,
            task_description=task.description,
            category=triage.category,
            success=True,
            method="micro-llm",
            file_path=str(path),
            line_number=task.line_number,
            details={
                "snippet": snippet.name,
                "start_line": snippet.start_line,
                "end_line": snippet.end_line,
                "tier": triage.tier,
            },
        )

    def _apply_magic_name(
        self,
        task: Task,
        triage: TaskTriage,
        path: Path,
        number: int,
        const_name: str,
    ) -> MicroFixResult:
        """Apply a constant-name replacement and insert the definition when needed."""
        original_text = path.read_text()
        lines = original_text.splitlines()
        if task.line_number is None or task.line_number > len(lines):
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="line not found",
            )

        line = lines[task.line_number - 1]
        new_line = re.sub(
            rf'(?<!["\'])\b{number}\b(?!["\'])',
            const_name,
            line,
            count=1,
        )
        if new_line == line:
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="could not replace number",
            )

        lines[task.line_number - 1] = new_line
        if not any(re.match(rf"^{re.escape(const_name)}\s*=\s*\d+\s*$", existing.strip()) for existing in lines):
            insert_at = _find_import_insert_point(lines)
            lines[insert_at:insert_at] = ["", "# Constants", f"{const_name} = {number}", ""]

        candidate = "\n".join(lines) + "\n"
        if not _validate_python(candidate):
            return MicroFixResult(
                task_id=task.id,
                task_description=task.description,
                category=triage.category,
                success=False,
                file_path=str(path),
                line_number=task.line_number,
                error="constant rewrite produced invalid python",
            )

        path.write_text(candidate)
        return MicroFixResult(
            task_id=task.id,
            task_description=task.description,
            category=triage.category,
            success=True,
            method="micro-llm",
            file_path=str(path),
            line_number=task.line_number,
            details={"constant": const_name, "number": number, "tier": triage.tier},
        )


def _find_import_insert_point(lines: list[str]) -> int:
    """Find the line after the last import statement."""
    last_import = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            last_import = index + 1
    return last_import


def _extract_first_int(text: str) -> int | None:
    """Extract the first integer from text."""
    match = re.search(r"\b(\d+)\b", text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _normalize_model_name(model: str) -> str:
    """Convert a user-facing model string into an Ollama model name."""
    return model.split("/", 1)[1] if model.startswith("ollama/") else model


def _strip_code_fences(text: str) -> str:
    """Remove markdown fences if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def _sanitize_constant_name(text: str, number: int) -> str:
    """Return a safe constant name from the model output."""
    candidate = text.strip().splitlines()[0].strip()
    candidate = re.sub(r"[^A-Za-z0-9_]+", "_", candidate).strip("_")
    if re.fullmatch(r"[A-Z][A-Z0-9_]+", candidate or ""):
        return candidate
    return f"MAGIC_{number}"


def _validate_python(source: str) -> bool:
    """Validate Python source syntax."""
    try:
        ast.parse(source)
        return True
    except SyntaxError:
        return False


def _coerce_task(task: Any) -> Task:
    """Convert different task dataclasses into a `todo_parser.Task`."""
    if isinstance(task, Task):
        return task

    file_path = getattr(task, "file_path", None) or getattr(task, "file", None)
    line_number = getattr(task, "line_number", None) or getattr(task, "line", None)
    description = getattr(task, "description", None) or getattr(task, "message", None) or ""
    task_id = getattr(task, "id", None) or f"{file_path}:{line_number or 0}"
    status = getattr(task, "status", None) or "pending"

    return Task(
        id=str(task_id),
        description=str(description),
        file_path=str(file_path) if file_path else None,
        line_number=int(line_number) if line_number else None,
        status=status,
    )
