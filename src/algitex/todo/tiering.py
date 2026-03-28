"""Task tiering and summary helpers for algitex TODO fixes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from algitex.tools.todo_parser import Task, TodoParser
from algitex.todo.classify import (
    KNOWN_MAGIC_CONSTANTS,
    TaskTriage,
    classify_message,
    classify_task,
)



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
