from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ServiceStatus:
    """Status of a single service."""

    name: str
    healthy: bool
    url: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def status_icon(self) -> str:
        """Get status icon for display."""
        return "✅" if self.healthy else "❌"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "healthy": self.healthy,
            "url": self.url,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "details": self.details,
        }
