"""Micro-LLM fixes for TODO tasks.

This module extracts the smallest useful code snippet around a TODO task,
feeds it to a local Ollama model, and applies the returned micro-fix back to
source code. It is intentionally conservative: only tasks that map to a single
function or a simple constant-name rewrite are handled here.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from algitex.tools.ollama import OllamaClient
from algitex.tools.todo_parser import TodoParser, Task
from algitex.todo.tiering import TaskTriage, classify_task
from algitex.todo.micro_models import FunctionSnippet, MicroFixResult
from algitex.todo.micro_extractor import FunctionExtractor
from algitex.todo.micro_prompts import MicroPromptBuilder
from algitex.todo.micro_utils import (
    MAX_MAGIC_TOKENS,
    MAX_REWRITE_TOKENS,
    TIMEOUT_SHORT,
    TIMEOUT_LONG,
    coerce_task,
    extract_first_int,
    find_import_insert_point,
    normalise_model_name,
    sanitize_constant_name,
    strip_code_fences,
    validate_python,
)


class MicroFixer:
    """Execute micro-LLM fixes on a TODO file."""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen3-coder:latest",
        workers: int = 4,
        dry_run: bool = True,
    ):
        self.ollama_url = ollama_url
        self.model = normalise_model_name(model)
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

        coerced_tasks = [coerce_task(item) for item in tasks]
        rewrite_tasks = [task for task in coerced_tasks if classify_task(task).category != "magic"]
        magic_tasks = [task for task in coerced_tasks if classify_task(task).category == "magic"]

        for task in sorted(rewrite_tasks, key=lambda item: item.line_number or 0, reverse=True):
            results.append(self.fix_task(task))

        for task in sorted(magic_tasks, key=lambda item: item.line_number or 0, reverse=True):
            results.append(self.fix_task(task))
        return results

    def fix_task(self, task: Task) -> MicroFixResult:
        """Fix a single micro task."""
        task = coerce_task(task)
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

        client = OllamaClient(host=self.ollama_url, default_model=self.model, timeout=TIMEOUT_LONG)
        try:
            messages = self.prompt_builder.build(triage, snippet, task)
            response = client.chat(messages=messages, model=self.model, temperature=0.0, max_tokens=MAX_REWRITE_TOKENS)
            content = strip_code_fences(response.content)
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

    def fix_tasks_detailed(self, tasks: list[Task], categories: set[str] | None = None) -> list[MicroFixResult]:
        """Run micro fixes on an already-parsed task list and return per-task results."""
        micro_tasks = [coerce_task(task) for task in tasks if classify_task(task).tier == "micro"]
        if categories:
            micro_tasks = [task for task in micro_tasks if classify_task(task).category in categories]

        if not micro_tasks:
            return []

        by_file_map: dict[str, list[Task]] = {}
        for task in micro_tasks:
            if not task.file_path:
                continue
            by_file_map.setdefault(task.file_path, []).append(task)

        results: list[MicroFixResult] = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {
                pool.submit(self.fix_file, Path(file_path), file_tasks): file_path
                for file_path, file_tasks in by_file_map.items()
            }
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception as exc:
                    print(f"  ✗ Micro fix failed: {exc}")

        return results

    def fix_tasks(self, tasks: list[Task], categories: set[str] | None = None) -> dict[str, int]:
        """Run micro fixes on an already-parsed task list."""
        micro_results = self.fix_tasks_detailed(tasks, categories=categories)
        if not micro_results:
            print("No micro-LLM tasks found.")
            return {"fixed": 0, "skipped": 0, "errors": 0}

        fixed = sum(1 for item in micro_results if item.success)
        skipped = sum(1 for item in micro_results if not item.success and not item.error)
        errors = sum(1 for item in micro_results if item.error)

        print(f"Micro LLM: fixed={fixed}, skipped={skipped}, errors={errors}")
        return {"fixed": fixed, "skipped": skipped, "errors": errors}

    def _fix_magic_name(self, task: Task, triage: TaskTriage, path: Path) -> MicroFixResult:
        """Ask the model for a constant name and apply it."""
        number = triage.number if triage.number is not None else extract_first_int(task.description)
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

        client = OllamaClient(host=self.ollama_url, default_model=self.model, timeout=TIMEOUT_SHORT)
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
            response = client.chat(messages=messages, model=self.model, temperature=0.0, max_tokens=MAX_MAGIC_TOKENS)
            const_name = sanitize_constant_name(response.content, number)
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
        if not validate_python(candidate):
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
            insert_at = find_import_insert_point(lines)
            lines[insert_at:insert_at] = ["", "# Constants", f"{const_name} = {number}", ""]

        candidate = "\n".join(lines) + "\n"
        if not validate_python(candidate):
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


__all__ = [
    "MicroFixer",
    "FunctionExtractor",
    "FunctionSnippet",
    "MicroFixResult",
    "MicroPromptBuilder",
]
