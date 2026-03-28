"""MicroTask API — atomic tasks for small LLMs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class TaskType(str, Enum):
    """Classification tiers for micro tasks."""

    UNUSED_IMPORT = "unused_import"
    RETURN_TYPE = "return_type"
    FSTRING = "fstring"
    KNOWN_MAGIC = "known_magic"
    SORT_IMPORTS = "sort_imports"
    TRAILING_WHITESPACE = "trailing_whitespace"
    UNKNOWN_MAGIC = "unknown_magic"
    DOCSTRING_FIX = "docstring_fix"
    VARIABLE_RENAME = "variable_rename"
    GUARD_CLAUSE = "guard_clause"
    TYPE_INFERENCE = "type_inference"
    DICT_DISPATCH = "dict_dispatch"
    EXTRACT_METHOD = "extract_method"
    ERROR_HANDLING = "error_handling"
    SPLIT_FUNCTION = "split_function"
    DEPENDENCY_CYCLE = "dependency_cycle"
    API_REDESIGN = "api_redesign"

    @property
    def tier(self) -> int:
        """Return the execution tier for this task type."""
        if self in _TIER_0_TASKS:
            return 0
        if self in _TIER_1_TASKS:
            return 1
        if self in _TIER_2_TASKS:
            return 2
        return 3

    @property
    def model_hint(self) -> str:
        """Return a rough model hint for the current tier."""
        return {
            0: "none",
            1: "qwen2.5-coder:7b",
            2: "qwen2.5-coder:14b",
            3: "qwen2.5-coder:70b",
        }[self.tier]

    @property
    def max_context_tokens(self) -> int:
        """Return the soft context budget for this tier."""
        return {
            0: 0,
            1: 1800,
            2: 4000,
            3: 12000,
        }[self.tier]

    @property
    def max_output_tokens(self) -> int:
        """Return the soft output budget for this tier."""
        return {
            0: 0,
            1: 256,
            2: 512,
            3: 1000,
        }[self.tier]


_TIER_0_TASKS = {
    TaskType.UNUSED_IMPORT,
    TaskType.RETURN_TYPE,
    TaskType.FSTRING,
    TaskType.KNOWN_MAGIC,
    TaskType.SORT_IMPORTS,
    TaskType.TRAILING_WHITESPACE,
}

_TIER_1_TASKS = {
    TaskType.UNKNOWN_MAGIC,
    TaskType.DOCSTRING_FIX,
    TaskType.VARIABLE_RENAME,
    TaskType.GUARD_CLAUSE,
    TaskType.TYPE_INFERENCE,
}

_TIER_2_TASKS = {
    TaskType.DICT_DISPATCH,
    TaskType.EXTRACT_METHOD,
    TaskType.ERROR_HANDLING,
    TaskType.SPLIT_FUNCTION,
    TaskType.DEPENDENCY_CYCLE,
    TaskType.API_REDESIGN,
}


@dataclass
class MicroTask:
    """Atomic unit of work for a single file change."""

    id: str
    type: TaskType
    file: str
    line_start: int
    line_end: int
    function_name: str = ""
    class_name: str = ""
    context: str = ""
    context_tokens: int = 0
    instruction: str = ""
    expected_format: str = "code"
    prefact_message: str = ""
    suggested_fix: str = ""
    status: str = "pending"
    fix_applied: str = ""
    model_used: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: float = 0.0
    context_start: int = 0
    context_end: int = 0

    @property
    def tier(self) -> int:
        """Return the task tier."""
        return self.type.tier

    @property
    def is_algorithmic(self) -> bool:
        """Return True when the task is deterministic."""
        return self.tier == 0

    @property
    def needs_llm(self) -> bool:
        """Return True when the task should go through an LLM phase."""
        return self.tier > 0

    @property
    def span(self) -> int:
        """Return the currently targeted line span."""
        return max(1, self.line_end - self.line_start + 1)


@dataclass
class MicroTaskBatch:
    """Tasks grouped by file for execution."""

    file: str
    tasks: list[MicroTask] = field(default_factory=list)
    status: str = "pending"

    @property
    def algo_tasks(self) -> list[MicroTask]:
        """Return deterministic tasks."""
        return [task for task in self.tasks if task.is_algorithmic]

    @property
    def llm_tasks(self) -> list[MicroTask]:
        """Return non-deterministic tasks."""
        return [task for task in self.tasks if task.needs_llm]

    def stats(self) -> dict[str, int | str]:
        """Return summary statistics for the batch."""
        tier_counts = defaultdict(int)
        for task in self.tasks:
            tier_counts[task.tier] += 1
        return {
            "file": self.file,
            "total": len(self.tasks),
            "tier_0": tier_counts.get(0, 0),
            "tier_1": tier_counts.get(1, 0),
            "tier_2": tier_counts.get(2, 0),
            "tier_3": tier_counts.get(3, 0),
            "algorithmic": len(self.algo_tasks),
            "llm": len(self.llm_tasks),
        }


def group_tasks_by_file(tasks: Iterable[MicroTask]) -> list[MicroTaskBatch]:
    """Group micro tasks by file path."""
    batches: dict[str, MicroTaskBatch] = {}
    for task in tasks:
        batches.setdefault(task.file, MicroTaskBatch(file=task.file)).tasks.append(task)
    return [batches[file_path] for file_path in sorted(batches)]


__all__ = [
    "MicroTask",
    "MicroTaskBatch",
    "TaskType",
    "group_tasks_by_file",
]
