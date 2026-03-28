"""Three-phase MicroTask executor."""

from __future__ import annotations

import ast
import re
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from algitex.microtask import MicroTask, MicroTaskBatch, TaskType, group_tasks_by_file
from algitex.microtask.prompts import PromptBuilder
from algitex.microtask.slicer import ContextSlicer
from algitex.nlp import sort_imports_in_path
from algitex.todo.fixer import TodoTask, fix_fstring, fix_magic_number, fix_module_block, fix_return_type, fix_unused_import
from algitex.todo.hybrid import RateLimiter
from algitex.tools.ollama import OllamaClient


@dataclass
class PhaseResult:
    """Summary for a single execution phase."""

    name: str
    total: int = 0
    fixed: int = 0
    skipped: int = 0
    errors: int = 0
    duration_ms: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def throughput(self) -> float:
        """Return tasks per second for the phase."""
        if self.duration_ms <= 0:
            return 0.0
        return self.total / (self.duration_ms / 1000.0)

    def as_dict(self) -> dict[str, int | float | str | list[str]]:
        return {
            "name": self.name,
            "total": self.total,
            "fixed": self.fixed,
            "skipped": self.skipped,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "throughput": self.throughput,
            "notes": self.notes,
        }


class MicroTaskExecutor:
    """Execute micro tasks in three tiers: algorithmic, small LLM, big LLM."""

    def __init__(
        self,
        project_path: str | Path = ".",
        ollama_url: str = "http://localhost:11434",
        algo_workers: int = 8,
        llm_workers: int = 4,
        rate_limit_rps: float = 10.0,
    ) -> None:
        self.project_path = Path(project_path)
        self.ollama_url = ollama_url
        self.algo_workers = max(1, algo_workers)
        self.llm_workers = max(1, llm_workers)
        self.rate_limiter = RateLimiter(rate=rate_limit_rps, burst=max(1, llm_workers))
        self.prompt_builder = PromptBuilder()
        self.slicer = ContextSlicer(self.project_path)
        self.client = OllamaClient(host=ollama_url, timeout=180.0)

    def execute(self, tasks: list[MicroTask], dry_run: bool = True) -> list[PhaseResult]:
        """Run all micro tasks in the three execution phases."""
        phase_0 = [task for task in tasks if task.tier == 0]
        phase_1 = [task for task in tasks if task.tier == 1]
        phase_2 = [task for task in tasks if task.tier == 2]
        phase_3 = [task for task in tasks if task.tier >= 3]

        results = [
            self._phase_algorithmic(phase_0, dry_run=dry_run),
            self._phase_llm(phase_1 + phase_2, dry_run=dry_run, name="Small LLM", workers=self.llm_workers),
            self._phase_llm(phase_3, dry_run=dry_run, name="Big LLM", workers=1),
        ]
        return results

    def group_by_file(self, tasks: list[MicroTask]) -> dict[str, MicroTaskBatch]:
        """Return file-grouped batches for planning or execution."""
        batches: dict[str, MicroTaskBatch] = {}
        for task in tasks:
            batches.setdefault(task.file, MicroTaskBatch(file=task.file)).tasks.append(task)
        return batches

    def _phase_algorithmic(self, tasks: list[MicroTask], dry_run: bool) -> PhaseResult:
        result = PhaseResult(name="Algorithmic", total=len(tasks))
        if not tasks:
            return result

        started = time.perf_counter()
        batches = group_tasks_by_file(tasks)

        with ThreadPoolExecutor(max_workers=self.algo_workers) as pool:
            futures = {pool.submit(self._process_algorithmic_batch, batch, dry_run): batch for batch in batches}
            for future in as_completed(futures):
                fixed, skipped, errors, note = future.result()
                result.fixed += fixed
                result.skipped += skipped
                result.errors += errors
                if note:
                    result.notes.append(note)

        result.duration_ms = (time.perf_counter() - started) * 1000
        return result

    def _process_algorithmic_batch(self, batch: MicroTaskBatch, dry_run: bool) -> tuple[int, int, int, str]:
        path = self._resolve_path(batch.file)
        if not path.exists():
            return 0, len(batch.tasks), 1, f"missing file: {batch.file}"

        if dry_run:
            fixed = sum(1 for task in batch.tasks if self._supports_algorithmic(task))
            skipped = len(batch.tasks) - fixed
            return fixed, skipped, 0, ""

        fixed = 0
        skipped = 0
        errors = 0
        note = ""

        line_tasks = [task for task in batch.tasks if task.type in {TaskType.UNUSED_IMPORT, TaskType.RETURN_TYPE, TaskType.KNOWN_MAGIC}]
        line_tasks.sort(key=lambda task: (task.context_start or task.line_start, task.context_end or task.line_end, task.line_start), reverse=True)

        for task in line_tasks:
            try:
                ok = self._apply_line_fix(path, task)
                if ok:
                    fixed += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                note = str(exc)

        fstring_tasks = [task for task in batch.tasks if task.type == TaskType.FSTRING]
        if fstring_tasks:
            try:
                ok = self._apply_fstring_fix(path, fstring_tasks)
                if ok:
                    fixed += len(fstring_tasks)
                else:
                    skipped += len(fstring_tasks)
            except Exception as exc:
                errors += len(fstring_tasks)
                note = str(exc)

        sort_tasks = [task for task in batch.tasks if task.type == TaskType.SORT_IMPORTS]
        if sort_tasks:
            try:
                stats = sort_imports_in_path(path, apply=True)
                if stats.get("changed", 0):
                    fixed += len(sort_tasks)
                else:
                    skipped += len(sort_tasks)
            except Exception as exc:
                errors += len(sort_tasks)
                note = str(exc)

        whitespace_tasks = [task for task in batch.tasks if task.type == TaskType.TRAILING_WHITESPACE]
        if whitespace_tasks:
            try:
                changed = self._strip_trailing_whitespace(path)
                if changed:
                    fixed += len(whitespace_tasks)
                else:
                    skipped += len(whitespace_tasks)
            except Exception as exc:
                errors += len(whitespace_tasks)
                note = str(exc)

        return fixed, skipped, errors, note

    def _phase_llm(self, tasks: list[MicroTask], dry_run: bool, name: str, workers: int) -> PhaseResult:
        result = PhaseResult(name=name, total=len(tasks))
        if not tasks:
            return result

        started = time.perf_counter()
        batches = group_tasks_by_file(tasks)

        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futures = {pool.submit(self._process_llm_batch, batch, dry_run): batch for batch in batches}
            for future in as_completed(futures):
                fixed, skipped, errors, note = future.result()
                result.fixed += fixed
                result.skipped += skipped
                result.errors += errors
                if note:
                    result.notes.append(note)

        result.duration_ms = (time.perf_counter() - started) * 1000
        return result

    def _process_llm_batch(self, batch: MicroTaskBatch, dry_run: bool) -> tuple[int, int, int, str]:
        path = self._resolve_path(batch.file)
        if not path.exists():
            return 0, len(batch.tasks), 1, f"missing file: {batch.file}"

        fixed = 0
        skipped = 0
        errors = 0
        note = ""

        for task in sorted(batch.llm_tasks, key=lambda item: (item.line_start, item.line_end), reverse=True):
            try:
                self.slicer.slice(task)
                prompt = self.prompt_builder.build(task)
                task.model_used = str(prompt["model"])
                task.tokens_in = task.context_tokens
                if dry_run:
                    task.status = "planned"
                    fixed += 1
                    continue

                wait = self.rate_limiter.acquire()
                if wait:
                    time.sleep(wait)

                response = self.client.chat(
                    messages=prompt["messages"],
                    model=str(prompt["model"]),
                    temperature=0.0,
                    max_tokens=task.type.max_output_tokens or None,
                )
                content = getattr(response, "content", "") or ""
                task.tokens_out = len(content.split())
                task.fix_applied = content
                started = time.perf_counter()
                ok = self._apply_llm_response(task, content)
                task.duration_ms = (time.perf_counter() - started) * 1000
                if ok:
                    task.status = "fixed"
                    fixed += 1
                else:
                    task.status = "skipped"
                    skipped += 1
            except Exception as exc:
                errors += 1
                note = str(exc)
                task.status = "error"
                task.fix_applied = ""
                task.duration_ms = 0.0

        return fixed, skipped, errors, note

    def _supports_algorithmic(self, task: MicroTask) -> bool:
        return task.type in {
            TaskType.UNUSED_IMPORT,
            TaskType.RETURN_TYPE,
            TaskType.FSTRING,
            TaskType.KNOWN_MAGIC,
            TaskType.SORT_IMPORTS,
            TaskType.TRAILING_WHITESPACE,
        }

    def _apply_line_fix(self, path: Path, task: MicroTask) -> bool:
        todo_task = TodoTask(
            file=str(path),
            line=task.line_start,
            message=task.prefact_message or task.instruction or task.context,
            category=self._todo_category(task),
        )
        fixer = {
            TaskType.UNUSED_IMPORT: fix_unused_import,
            TaskType.RETURN_TYPE: fix_return_type,
            TaskType.KNOWN_MAGIC: fix_magic_number,
        }.get(task.type)
        if fixer is None:
            return False
        return fixer(path, todo_task)

    def _apply_fstring_fix(self, path: Path, tasks: list[MicroTask]) -> bool:
        if any("module execution block" in task.prefact_message.lower() or "if __name__" in task.prefact_message.lower() for task in tasks):
            return fix_module_block(path, TodoTask(file=str(path), line=tasks[0].line_start, message=tasks[0].prefact_message, category="module_block"))
        return fix_fstring(path, TodoTask(file=str(path), line=tasks[0].line_start, message=tasks[0].prefact_message, category="fstring"))

    def _apply_llm_response(self, task: MicroTask, content: str) -> bool:
        path = self._resolve_path(task.file)
        if not content.strip():
            return False
        if task.type == TaskType.UNKNOWN_MAGIC:
            return self._apply_magic_name(path, task, content)
        return self._apply_rewrite(path, task, content)

    def _apply_magic_name(self, path: Path, task: MicroTask, content: str) -> bool:
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        number = self._first_int(task.prefact_message) or self._first_int(task.context) or self._first_int(content)
        if number is None:
            return False
        const_name = self._sanitize_constant_name(content, number)

        if task.context_start and task.context_end:
            snippet = "\n".join(lines[task.context_start - 1 : task.context_end])
            new_snippet = re.sub(rf"(?<![\"\'])\b{number}\b(?![\"\'])", const_name, snippet, count=1)
            if new_snippet == snippet:
                return False
            lines[task.context_start - 1 : task.context_end] = new_snippet.splitlines()
            if not any(re.match(rf"^{re.escape(const_name)}\s*=\s*\d+\s*$", existing.strip()) for existing in lines):
                insert_at = self._find_import_insert_point(lines)
                lines[insert_at:insert_at] = ["", "# Constants", f"{const_name} = {number}", ""]
            candidate = "\n".join(lines) + ("\n" if source.endswith("\n") else "")
            if not self._validate_python(candidate):
                return False
            path.write_text(candidate, encoding="utf-8")
            return True

        target_line = task.line_start
        if target_line <= 0 or target_line > len(lines):
            return False
        new_line = re.sub(rf"(?<![\"\'])\b{number}\b(?![\"\'])", const_name, lines[target_line - 1], count=1)
        if new_line == lines[target_line - 1]:
            return False
        lines[target_line - 1] = new_line
        candidate = "\n".join(lines) + ("\n" if source.endswith("\n") else "")
        if not self._validate_python(candidate):
            return False
        path.write_text(candidate, encoding="utf-8")
        return True

    def _apply_rewrite(self, path: Path, task: MicroTask, content: str) -> bool:
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        replacement = self._strip_code_fences(content).strip()
        if not replacement:
            return False

        start = task.context_start or task.line_start
        end = task.context_end or task.line_end
        if start <= 0 or end <= 0 or start > len(lines) or end > len(lines) or start > end:
            return False

        lines[start - 1 : end] = replacement.splitlines()
        candidate = "\n".join(lines) + ("\n" if source.endswith("\n") else "")
        if path.suffix == ".py" and not self._validate_python(candidate):
            return False
        path.write_text(candidate, encoding="utf-8")
        return True

    def _strip_trailing_whitespace(self, path: Path) -> bool:
        source = path.read_text(encoding="utf-8")
        stripped = "\n".join(line.rstrip() for line in source.splitlines())
        if source.endswith("\n"):
            stripped += "\n"
        if stripped == source:
            return False
        path.write_text(stripped, encoding="utf-8")
        return True

    def _todo_category(self, task: MicroTask) -> str:
        return {
            TaskType.UNUSED_IMPORT: "unused_import",
            TaskType.RETURN_TYPE: "return_type",
            TaskType.FSTRING: "fstring",
            TaskType.KNOWN_MAGIC: "magic",
        }.get(task.type, task.type.value)

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path
        candidate = self.project_path / path
        if candidate.exists():
            return candidate
        return path

    def _find_import_insert_point(self, lines: list[str]) -> int:
        last_import = 0
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                last_import = index + 1
        return last_import

    def _first_int(self, text: str) -> int | None:
        match = re.search(r"\b(\d+)\b", text)
        if not match:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    def _sanitize_constant_name(self, text: str, number: int) -> str:
        candidate = text.strip().splitlines()[0].strip() if text.strip() else ""
        candidate = re.sub(r"[^A-Za-z0-9_]+", "_", candidate).strip("_")
        if re.fullmatch(r"[A-Z][A-Z0-9_]+", candidate or ""):
            return candidate
        return f"MAGIC_{number}"

    def _strip_code_fences(self, text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    def _validate_python(self, source: str) -> bool:
        try:
            ast.parse(source)
            return True
        except SyntaxError:
            return False

    def close(self) -> None:
        """Close the shared Ollama client."""
        self.client.close()


__all__ = ["MicroTaskExecutor", "PhaseResult"]
