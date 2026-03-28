"""Metrics collection and reporting for algitex.

Tracks:
- Token usage per tier (algorithmic, micro, big LLM)
- Success/failure rates
- Cache hit rates
- Execution time per task type
- Cost estimates

Usage:
    from algitex.metrics import MetricsCollector, MetricsReporter
    
    metrics = MetricsCollector()
    metrics.record_llm_call(tier="micro", tokens_in=500, tokens_out=200, success=True)
    
    reporter = MetricsReporter(metrics)
    reporter.print_dashboard()
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict


@dataclass
class LLMCall:
    """Single LLM call record."""
    timestamp: float
    tier: str  # "algorithm", "micro", "big"
    model: str
    tokens_in: int
    tokens_out: int
    duration_ms: float
    success: bool
    cached: bool = False
    task_category: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FixResult:
    """Single fix execution record."""
    timestamp: float
    tier: str
    category: str
    file: str
    line: int
    success: bool
    duration_ms: float
    used_llm: bool = False


class MetricsCollector:
    """Collect metrics during algitex operations."""
    
    # Approximate costs per 1M tokens (USD)
    COST_RATES = {
        "qwen3-coder:latest": 0.0,  # Local = free
        "qwen2.5-coder:3b": 0.0,
        "qwen3-coder:latest": 0.0,
        "codellama:7b": 0.0,
        "deepseek-coder:6.7b": 0.0,
        "llama3:8b": 0.0,
        "claude-3-5-sonnet": 3.0,  # $3/M input, $15/M output
        "claude-3-haiku": 0.25,
        "gpt-4o": 2.5,
        "gpt-4o-mini": 0.15,
    }
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path(".algitex/metrics.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.llm_calls: List[LLMCall] = []
        self.fix_results: List[FixResult] = []
        self._session_start = time.time()
    
    def record_llm_call(
        self,
        tier: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        duration_ms: float,
        success: bool,
        cached: bool = False,
        task_category: str = "",
    ) -> None:
        """Record an LLM API call."""
        self.llm_calls.append(LLMCall(
            timestamp=time.time(),
            tier=tier,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            duration_ms=duration_ms,
            success=success,
            cached=cached,
            task_category=task_category,
        ))
    
    def record_fix(
        self,
        tier: str,
        category: str,
        file: str,
        line: int,
        success: bool,
        duration_ms: float,
        used_llm: bool = False,
    ) -> None:
        """Record a fix execution."""
        self.fix_results.append(FixResult(
            timestamp=time.time(),
            tier=tier,
            category=category,
            file=file,
            line=line,
            success=success,
            duration_ms=duration_ms,
            used_llm=used_llm,
        ))
    
    def get_tier_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by tier."""
        stats = defaultdict(lambda: {
            "calls": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "success": 0,
            "failure": 0,
            "cached": 0,
            "duration_ms": 0,
        })
        
        for call in self.llm_calls:
            s = stats[call.tier]
            s["calls"] += 1
            s["tokens_in"] += call.tokens_in
            s["tokens_out"] += call.tokens_out
            s["success" if call.success else "failure"] += 1
            s["cached"] += 1 if call.cached else 0
            s["duration_ms"] += call.duration_ms
        
        for fix in self.fix_results:
            s = stats[fix.tier]
            s["success" if fix.success else "failure"] += 1
            s["duration_ms"] += fix.duration_ms
        
        return dict(stats)
    
    def estimate_cost(self) -> Dict[str, float]:
        """Estimate total cost based on token usage."""
        costs = defaultdict(float)
        
        for call in self.llm_calls:
            if call.cached:
                continue  # Cached = free
            
            rate_in = self.COST_RATES.get(call.model, 0.0)
            rate_out = rate_in * 5  # Output typically 5x more expensive
            
            cost = (call.tokens_in / 1_000_000 * rate_in) + (call.tokens_out / 1_000_000 * rate_out)
            costs[call.tier] += cost
            costs["total"] += cost
        
        return dict(costs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete metrics summary."""
        tier_stats = self.get_tier_stats()
        costs = self.estimate_cost()
        session_duration = time.time() - self._session_start
        
        total_calls = len(self.llm_calls)
        cached_calls = sum(1 for c in self.llm_calls if c.cached)
        
        return {
            "session_duration_sec": round(session_duration, 2),
            "llm_calls": total_calls,
            "cached_calls": cached_calls,
            "cache_hit_rate": cached_calls / total_calls if total_calls else 0,
            "tier_stats": tier_stats,
            "estimated_cost_usd": round(costs.get("total", 0), 4),
            "cost_by_tier": {k: round(v, 4) for k, v in costs.items() if k != "total"},
            "fix_attempts": len(self.fix_results),
            "fix_success_rate": sum(1 for f in self.fix_results if f.success) / len(self.fix_results) if self.fix_results else 0,
        }
    
    def save(self) -> None:
        """Persist metrics to disk."""
        data = {
            "summary": self.get_summary(),
            "llm_calls": [c.to_dict() for c in self.llm_calls[-1000:]],  # Keep last 1000
            "fix_results": [asdict(f) for f in self.fix_results[-1000:]],
        }
        self.storage_path.write_text(json.dumps(data, indent=2))
    
    def load(self) -> None:
        """Load previous metrics from disk."""
        if not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            # Restore limited history
            for call_data in data.get("llm_calls", [])[-500:]:
                self.llm_calls.append(LLMCall(**call_data))
            for fix_data in data.get("fix_results", [])[-500:]:
                self.fix_results.append(FixResult(**fix_data))
        except (json.JSONDecodeError, TypeError):
            pass  # Corrupted file, start fresh
    
    def reset(self) -> None:
        """Clear all metrics."""
        self.llm_calls.clear()
        self.fix_results.clear()
        self._session_start = time.time()


class MetricsReporter:
    """Generate reports and dashboards from metrics."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def print_dashboard(self, console=None) -> None:
        """Print Rich dashboard to console."""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            
            console = console or Console()
            summary = self.collector.get_summary()
            tier_stats = summary["tier_stats"]
            
            # Main stats panel
            main_text = (
                f"Session: {summary['session_duration_sec']:.0f}s | "
                f"LLM Calls: {summary['llm_calls']} | "
                f"Cached: {summary['cache_hit_rate']:.1%} | "
                f"Fixes: {summary['fix_attempts']} | "
                f"Success: {summary['fix_success_rate']:.1%}"
            )
            console.print(Panel(main_text, title="Algitex Metrics", border_style="blue"))
            
            # Tier breakdown table
            table = Table(title="Tier Performance")
            table.add_column("Tier", style="bold")
            table.add_column("Calls", justify="right")
            table.add_column("Tokens", justify="right")
            table.add_column("Cached", justify="right")
            table.add_column("Success", justify="right")
            table.add_column("Cost", justify="right")
            
            costs = self.collector.estimate_cost()
            
            for tier in ["algorithm", "micro", "big"]:
                stats = tier_stats.get(tier, {})
                calls = stats.get("calls", 0)
                tokens = stats.get("tokens_in", 0) + stats.get("tokens_out", 0)
                cached = stats.get("cached", 0)
                success = stats.get("success", 0)
                cost = costs.get(tier, 0)
                
                tier_label = {"algorithm": "0-Algorithm", "micro": "1-Micro", "big": "2-Big"}.get(tier, tier)
                table.add_row(
                    tier_label,
                    str(calls),
                    f"{tokens:,}" if tokens else "-",
                    f"{cached}" if cached else "-",
                    str(success),
                    f"${cost:.4f}" if cost else "-",
                )
            
            console.print(table)
            console.print(f"\n[dim]Estimated total cost: ${summary['estimated_cost_usd']:.4f}[/]")
            
        except ImportError:
            # Fallback to plain text
            summary = self.collector.get_summary()
            print("=" * 50)
            print("ALGITEX METRICS")
            print("=" * 50)
            print(f"Session: {summary['session_duration_sec']:.0f}s")
            print(f"LLM Calls: {summary['llm_calls']} (cached: {summary['cache_hit_rate']:.1%})")
            print(f"Fixes: {summary['fix_attempts']} (success: {summary['fix_success_rate']:.1%})")
            print(f"Est. Cost: ${summary['estimated_cost_usd']:.4f}")
    
    def export_csv(self, path: str) -> None:
        """Export metrics to CSV for analysis."""
        import csv
        
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "tier", "model", "tokens_in", "tokens_out", 
                           "duration_ms", "success", "cached", "category"])
            
            for call in self.collector.llm_calls:
                writer.writerow([
                    call.timestamp,
                    call.tier,
                    call.model,
                    call.tokens_in,
                    call.tokens_out,
                    call.duration_ms,
                    call.success,
                    call.cached,
                    call.task_category,
                ])


# Global metrics instance for convenience
_global_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector()
        _global_metrics.load()
    return _global_metrics


def reset_metrics() -> None:
    """Reset global metrics."""
    global _global_metrics
    _global_metrics = MetricsCollector()
