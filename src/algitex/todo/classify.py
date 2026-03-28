"""Task classification using pattern dispatch.

Replaces complex if/elif chains with a dispatch table for O(1) lookup.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


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


TIER_LABELS = {
    "algorithm": "Algorithm",
    "micro": "Small LLM",
    "big": "Big LLM",
}

# ─── Dispatch table: pattern → (category, tier, reason) ─────────

_PATTERNS: list[tuple[str, str, str, str]] = [
    # (regex_pattern, category, tier, reason)
    (r"unused import", "unused_import", "algorithm", "deterministic import cleanup"),
    (r"unused\s+\w+\s+imported from", "unused_import", "algorithm", "deterministic import cleanup"),
    (r"unused import:", "unused_import", "algorithm", "deterministic import cleanup"),
    (r"return type", "return_type", "algorithm", "simple annotation insertion"),
    (r"missing return", "return_type", "algorithm", "simple annotation insertion"),
    (r"->\s*none", "return_type", "algorithm", "simple annotation insertion"),
    (r"->\s*bool", "return_type", "algorithm", "simple annotation insertion"),
    (r"->\s*str", "return_type", "algorithm", "simple annotation insertion"),
    (r"->\s*int", "return_type", "algorithm", "simple annotation insertion"),
    (r"->\s*list", "return_type", "algorithm", "simple annotation insertion"),
    (r"->\s*dict", "return_type", "algorithm", "simple annotation insertion"),
    (r"f-string", "fstring", "algorithm", "deterministic string rewrite"),
    (r"string concatenation", "fstring", "algorithm", "deterministic string rewrite"),
    (r"can be converted to f-string", "fstring", "algorithm", "deterministic string rewrite"),
    (r"module execution block", "module_block", "algorithm", "append module guard"),
    (r"standalone main function", "module_block", "algorithm", "append module guard"),
    (r"if __name__", "module_block", "algorithm", "append module guard"),
    (r"docstring", "docstring", "micro", "LLM-style prose rewrite"),
    (r"sphinx", "docstring", "micro", "LLM-style prose rewrite"),
    (r"verbose", "docstring", "micro", "LLM-style prose rewrite"),
    (r"rename", "rename", "micro", "naming refinement"),
    (r"descriptive name", "rename", "micro", "naming refinement"),
    (r"variable name", "rename", "micro", "naming refinement"),
    (r"name to", "rename", "micro", "naming refinement"),
    (r"guard clause", "guard_clause", "micro", "single-guard insertion"),
    (r"input validation", "guard_clause", "micro", "single-guard insertion"),
    (r"validate", "guard_clause", "micro", "single-guard insertion"),
    (r"dispatch", "dispatch", "micro", "small control-flow refactor"),
    (r"if/elif", "dispatch", "micro", "small control-flow refactor"),
    (r"dictionary", "dispatch", "micro", "small control-flow refactor"),
    (r"dependency cycle", "dependency_cycle", "big", "architectural dependency issue"),
    (r"circular dependency", "dependency_cycle", "big", "architectural dependency issue"),
    (r"architecture", "architecture", "big", "architectural redesign"),
    (r"api redesign", "architecture", "big", "architectural redesign"),
    (r"split", "split_function", "big", "large-scale refactor needed"),
    (r"god function", "split_function", "big", "large-scale refactor needed"),
    (r"refactor", "split_function", "big", "large-scale refactor needed"),
    (r"too large", "split_function", "big", "large-scale refactor needed"),
]

# Known magic constants for automatic replacement
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


def _first_int(text: str) -> int | None:
    """Extract the first integer from text."""
    match = re.search(r"\b(\d+)\b", text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def classify_message(message: str) -> TaskTriage:
    """Classify a TODO message using pattern dispatch table.
    
    CC: 4 (1 loop + 3 branches in fallback)
    Was: CC ~50 (25+ if/elif branches)
    """
    msg_lower = message.lower()
    
    # Primary dispatch: pattern matching
    for pattern, category, tier, reason in _PATTERNS:
        if re.search(pattern, msg_lower):
            return TaskTriage(category=category, tier=tier, reason=reason)
    
    # Secondary: magic number detection
    number = _first_int(message)
    if "magic number" in msg_lower or "named constant" in msg_lower or (number is not None and "constant" in msg_lower):
        if number is not None and number in KNOWN_MAGIC_CONSTANTS:
            return TaskTriage(
                category="magic_known",
                tier="algorithm",
                reason=f"known constant {number} -> {KNOWN_MAGIC_CONSTANTS[number]}",
                number=number,
            )
        return TaskTriage(category="magic", tier="micro", reason="needs naming help", number=number)
    
    # Fallback: other/big tier
    return TaskTriage(category="other", tier="big", reason="needs architectural or semantic review")


def classify_task(task: Any) -> TaskTriage:
    """Classify a task-like object."""
    message = getattr(task, "message", None) or getattr(task, "description", None)
    return classify_message(str(message or ""))


__all__ = ["TaskTriage", "classify_message", "classify_task", "KNOWN_MAGIC_CONSTANTS"]
