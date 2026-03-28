"""LLM cost & performance telemetry for algitex pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import time
from typing import Optional, Dict, Any, List


@dataclass
class TraceSpan:
    """Single operation span."""
    name: str
    tool: str
    started: float = field(default_factory=time.time)
    ended: float = 0
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0
    model: str = ""
    status: str = "running"  # running | ok | error
    error: str = ""

    @property
    def duration_s(self) -> float:
        return (self.ended or time.time()) - self.started

    def finish(self, status="ok", **kwargs):
        self.ended = time.time()
        self.status = status
        for k, v in kwargs.items():
            setattr(self, k, v)


class Telemetry:
    """Track costs, tokens, time across an algitex pipeline run."""

    def __init__(self, project_name: str, run_id: Optional[str] = None):
        self.project = project_name
        self.run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.spans: List[TraceSpan] = []
        self._langfuse = None  # lazy init

    def span(self, name: str, tool: str = "algitex") -> TraceSpan:
        """Create a new span for tracking."""
        s = TraceSpan(name=name, tool=tool)
        self.spans.append(s)
        return s

    # ─── Aggregates ──────────────────────────
    @property
    def total_cost(self) -> float:
        return sum(s.cost_usd for s in self.spans)

    @property
    def total_tokens(self) -> int:
        return sum(s.tokens_in + s.tokens_out for s in self.spans)

    @property
    def total_duration(self) -> float:
        return sum(s.duration_s for s in self.spans)

    @property
    def error_count(self) -> int:
        return sum(1 for s in self.spans if s.status == "error")

    def summary(self) -> Dict[str, Any]:
        """Get a summary of the telemetry data."""
        return {
            "run_id": self.run_id,
            "project": self.project,
            "spans": len(self.spans),
            "total_cost_usd": round(self.total_cost, 4),
            "total_tokens": self.total_tokens,
            "total_duration_s": round(self.total_duration, 1),
            "errors": self.error_count,
            "models_used": list({s.model for s in self.spans if s.model}),
            "tools_used": list({s.tool for s in self.spans}),
        }

    # ─── Langfuse integration (optional) ─────────────
    def push_to_langfuse(self):
        """Push traces to Langfuse for visualization."""
        try:
            from langfuse import Langfuse
            lf = Langfuse()
            trace = lf.trace(name=f"algitex-{self.run_id}")
            for s in self.spans:
                trace.generation(
                    name=s.name,
                    model=s.model,
                    input={"tool": s.tool},
                    output={"status": s.status},
                    usage={"input": s.tokens_in, "output": s.tokens_out},
                    metadata={"cost_usd": s.cost_usd, "duration": s.duration_s},
                )
            lf.flush()
        except ImportError:
            pass  # Langfuse optional

    # ─── Local persistence ───────────────────────────
    def save(self, output_dir: str = ".algitex"):
        """Save telemetry data to local file."""
        path = Path(output_dir) / "telemetry" / f"{self.run_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save detailed spans
        detailed_data = {
            "summary": self.summary(),
            "spans": [
                {
                    "name": s.name,
                    "tool": s.tool,
                    "started": s.started,
                    "ended": s.ended,
                    "duration_s": s.duration_s,
                    "tokens_in": s.tokens_in,
                    "tokens_out": s.tokens_out,
                    "cost_usd": s.cost_usd,
                    "model": s.model,
                    "status": s.status,
                    "error": s.error,
                }
                for s in self.spans
            ]
        }
        
        path.write_text(json.dumps(detailed_data, indent=2))

    def report(self) -> str:
        """Generate a human-readable report."""
        s = self.summary()
        return (
            f"Run {s['run_id']}: {s['spans']} operations, "
            f"${s['total_cost_usd']}, {s['total_tokens']} tokens, "
            f"{s['total_duration_s']}s, {s['errors']} errors"
        )
