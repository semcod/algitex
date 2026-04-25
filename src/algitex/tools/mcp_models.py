"""Data models for MCP service definitions."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MCPService:
    """Definition of an MCP service."""

    name: str
    command: List[str]
    port: Optional[int] = None
    health_endpoint: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    process: Optional[subprocess.Popen] = field(default=None, init=False)
    ready: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.port and not self.health_endpoint:
            self.health_endpoint = f"http://localhost:{self.port}/health"
