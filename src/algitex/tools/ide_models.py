"""Data models for IDE integration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class IDETool:
    """IDE tool configuration."""
    name: str
    command: str
    install_command: str
    env_vars: Dict[str, str] = None
    model_prefix: str = ""

    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}
