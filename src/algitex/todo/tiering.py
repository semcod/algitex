"""Task tiering and summary helpers for algitex TODO fixes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from algitex.tools.todo_parser import Task, TodoParser


KNOWN_MAGIC_CONSTANTS: dict[int, str] = {
    200: "HTTP_OK",
    404: "HTTP_NOT_FOUND",
    429: "HTTP_TOO_MANY_REQUESTS",
    500: "HTTP_SERVER_ERROR",
    8080: "DEFAULT_PORT",
    8001: "MCP_DEFAULT_PORT",
    8002: "MCP_SECONDARY_PORT",
    4000: "PROXYM_PORT",
    11434: "OLLAMA_PORT",
    120: "DEFAULT_TIMEOUT_S",
    30: "SHORT_TIMEOUT_S",
    150: "MAX_TOKENS_DEFAULT",
    5000: "BATCH_SIZE_DEFAULT",
}

ALGO_CATEGORIES = frozenset(
    {
        "unused_import",
        "return_type",
        "fstring",
        "module_block",
        "magic_known",
    }
)

MICRO_CATEGORIES = frozenset(
    {
        "magic",
        "docstring",
        "rename",
        "guard_clause",
        "dispatch",
    }
)

BIG_CATEGORIES = frozenset(
    {
        "split_function",
        "dependency_cycle",
        "architecture",
        "other",
    }
)

TIER_LABELS = {
    "algorithm": "Algorithm",
    "micro": "Small LLM",
    "big": "Big LLM",
}


@dataclass(frozen=True)
class TaskTriage:
    """Classification result for a single TODO task."""

    category: str
    tier: str
    reason: str = ""
    number: int | None = None

    @property
    def tier_label(self) -> str:
        """Human-friendly tier label."""
        return TIER_LABELS.get(self.tier, self.tier.title())

    @property
    def is_algorithmic(self) -> bool:
        """Return True for deterministic fixes."""
        return self.tier == "algorithm"

    @property
    def is_micro(self) -> bool:
        """Return True for small-LLM fixes."""
        return self.tier == "micro"

    @property
    def is_big(self) -> bool:
        """Return True for large-LLM fixes."""
        return self.tier == "big"


@dataclass
class TierSummary:
    """Aggregated classification summary for a TODO list."""

    total: int = 0
    tier_counts: dict[str, int] = field(
        default_factory=lambda: {"algorithm": 0, "micro": 0, "big": 0}
    )
    category_counts: dict[str, int] = field(default_factory=dict)
    items: list[TaskTriage] = field(default_factory=list)

    def add(self, triage: TaskTriage) -> None:
        """Add a classification entry."""
        self.total += 1
        self.tier_counts[triage.tier] = self.tier_counts.get(triage.tier, 0) + 1
        self.category_counts[triage.category] = self.category_counts.get(triage.category, 0) + 1
        self.items.append(triage)

    @property
    def algorithmic(self) -> int:
        """Return algorithmic task count."""
        return self.tier_counts.get("algorithm", 0)

    @property
    def micro(self) -> int:
        """Return small-LLM task count."""
        return self.tier_counts.get("micro", 0)

    @property
    def big(self) -> int:
        """Return large-LLM task count."""
        return self.tier_counts.get("big", 0)

    def tier_percent(self, tier: str) -> int:
        """Return integer percentage for a tier."""
        if self.total == 0:
            return 0
        return int(round(self.tier_counts.get(tier, 0) * 100 / self.total))

    def top_categories(self, limit: int = 12) -> list[tuple[str, int]]:
        """Return the most common categories."""
        return sorted(
            self.category_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:limit]


def _first_int(text: str) -> int | None:
    """Extract the first integer from text."""
    match = re.search(r"\b(\d+)\b", text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _normalise_task_message(task_or_message: Any) -> str:
    """Return the textual message for a task-like object."""
    if isinstance(task_or_message, str):
        return task_or_message
    message = getattr(task_or_message, "message", None) or getattr(task_or_message, "description", None)
    return str(message or "")


def classify_message(message: str) -> TaskTriage:
    """Classify a TODO message into a category and tier."""
    msg = message.strip()
    lowered = msg.lower()
    number = _first_int(msg)

    if "unused import" in lowered or ("unused" in lowered and "import" in lowered):
        return TaskTriage(category="unused_import", tier="algorithm", reason="deterministic import cleanup")

    if (
        "return type" in lowered
        or "missing return" in lowered
        or "-> none" in lowered
        or "-> bool" in lowered
        or "-> str" in lowered
        or "-> int" in lowered
        or "-> list" in lowered
        or "-> dict" in lowered
    ):
        return TaskTriage(category="return_type", tier="algorithm", reason="simple annotation insertion")

    if "f-string" in lowered or "string concatenation" in lowered or "can be converted to f-string" in lowered:
        return TaskTriage(category="fstring", tier="algorithm", reason="deterministic string rewrite")

    if (
        "module execution block" in lowered
        or "standalone main function" in lowered
        or "if __name__" in lowered
    ):
        return TaskTriage(category="module_block", tier="algorithm", reason="append module guard")

    if "magic number" in lowered or "named constant" in lowered or (number is not None and "constant" in lowered):
        if number is not None and number in KNOWN_MAGIC_CONSTANTS:
            return TaskTriage(
                category="magic_known",
                tier="algorithm",
                reason=f"known constant {number} -> {KNOWN_MAGIC_CONSTANTS[number]}",
                number=number,
            )
        return TaskTriage(category="magic", tier="micro", reason="needs naming help", number=number)

    if "docstring" in lowered or "sphinx" in lowered or "verbose" in lowered:
        return TaskTriage(category="docstring", tier="micro", reason="LLM-style prose rewrite")

    if "rename" in lowered or "descriptive name" in lowered or "variable name" in lowered or "name to" in lowered:
        return TaskTriage(category="rename", tier="micro", reason="naming refinement")

    if "guard clause" in lowered or "input validation" in lowered or "validate" in lowered:
        return TaskTriage(category="guard_clause", tier="micro", reason="single-guard insertion")

    if "dispatch" in lowered or "if/elif" in lowered or "dictionary" in lowered:
        return TaskTriage(category="dispatch", tier="micro", reason="small control-flow refactor")

    if (
        "split" in lowered
        or "god function" in lowered
        or "dependency cycle" in lowered
        or "circular dependency" in lowered
        or "architecture" in lowered
        or "api redesign" in lowered
        or "refactor" in lowered
        or "too large" in lowered
    ):
        if "dependency" in lowered and ("cycle" in lowered or "circular" in lowered):
            return TaskTriage(category="dependency_cycle", tier="big", reason="architectural dependency issue")
        if "architecture" in lowered or "api redesign" in lowered:
            return TaskTriage(category="architecture", tier="big", reason="architectural redesign")
        return TaskTriage(category="split_function", tier="big", reason="large-scale refactor needed")

    return TaskTriage(category="other", tier="big", reason="needs architectural or semantic review")


def classify_task(task: Any) -> TaskTriage:
    """Classify a task-like object."""
    return classify_message(_normalise_task_message(task))


def summarise_tasks(tasks: Iterable[Any]) -> TierSummary:
    """Summarise a list of tasks by category and tier."""
    summary = TierSummary()
    for task in tasks:
        summary.add(classify_task(task))
    return summary


# Backwards-compatible alias with American spelling.
summarize_tasks = summarise_tasks


def load_todo_tasks(todo_path: str | Path = "TODO.md") -> list[Task]:
    """Parse TODO tasks from a file."""
    return TodoParser(todo_path).parse()


def filter_tasks(
    tasks: Iterable[Any],
    *,
    tiers: set[str] | None = None,
    categories: set[str] | None = None,
) -> list[Any]:
    """Filter tasks by tier and/or category."""
    filtered: list[Any] = []
    for task in tasks:
        triage = classify_task(task)
        if tiers and triage.tier not in tiers:
            continue
        if categories and triage.category not in categories:
            continue
        filtered.append(task)
    return filtered


def partition_tasks(tasks: Iterable[Any]) -> dict[str, list[Any]]:
    """Partition tasks by tier."""
    buckets = {"algorithm": [], "micro": [], "big": []}
    for task in tasks:
        triage = classify_task(task)
        buckets.setdefault(triage.tier, []).append(task)
    return buckets
