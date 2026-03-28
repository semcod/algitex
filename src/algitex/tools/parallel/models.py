"""Data models for parallel task coordination — region-based conflict-free execution."""
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class RegionType(Enum):
    """Types of code regions that can be locked."""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    BLOCK = "block"  # top-level statements


@dataclass
class CodeRegion:
    """An AST-level lockable region within a file."""
    file: str
    name: str  # e.g. "Project.status" or "parse_token"
    type: RegionType
    start_line: int
    end_line: int
    signature_hash: str  # Hash of signature to detect line drift
    dependencies: List[str] = field(default_factory=list)  # regions this one imports/calls
    shadow_conflicts: List[str] = field(default_factory=list)  # shared imports/constants

    @property
    def key(self) -> str:
        return f"{self.file}::{self.name}"

    def compute_signature_hash(self, source: str) -> str:
        """Compute hash of function/class signature to track changes."""
        lines = source.split('\n')[self.start_line-1:self.end_line]
        signature = '\n'.join(lines[:min(5, len(lines))])  # First 5 lines as signature
        return hashlib.sha256(signature.encode()).hexdigest()[:16]


@dataclass
class TaskAssignment:
    """A ticket assigned to a specific agent with locked regions."""
    ticket_id: str
    agent_id: str
    worktree: str
    regions: List[CodeRegion]  # Locked exclusively
    status: str = "pending"  # pending | running | done | conflict


@dataclass
class MergeResult:
    """Result of merging agent worktrees back to main."""
    agent_id: str
    ticket_id: str
    status: str  # clean | conflict | semantic_conflict | shadow_conflict
    files_changed: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    line_drift_detected: bool = False
