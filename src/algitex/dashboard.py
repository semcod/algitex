"""Real-time TUI dashboard for algitex using Rich.

Provides live monitoring of:
- Cache performance (hit rate, entries, size)
- Tier throughput (algorithm, micro, big)
- Current operations progress
- System resource usage

Usage:
    from algitex.dashboard import LiveDashboard
    
    dashboard = LiveDashboard()
    dashboard.start()
    
    # Update metrics
    dashboard.update_cache_stats(hits=100, misses=10, entries=50)
    dashboard.update_tier_progress("micro", current=10, total=50)
    
    dashboard.stop()
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Callable
from collections import deque

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.layout import Layout


@dataclass
class TierState:
    """State tracking for a single tier."""
    name: str
    current: int = 0
    total: int = 0
    success: int = 0
    failed: int = 0
    throughput: float = 0.0
    active: bool = False
    
    @property
    def percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100
    
    @property
    def eta_seconds(self) -> float:
        if self.throughput <= 0 or self.current >= self.total:
            return 0.0
        remaining = self.total - self.current
        return remaining / self.throughput


@dataclass
class CacheState:
    """State tracking for cache metrics."""
    hits: int = 0
    misses: int = 0
    entries: int = 0
    size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / 1024 / 1024


class LiveDashboard:
    """Live Rich dashboard for monitoring algitex operations."""
    
    def __init__(self, refresh_rate: float = 1.0):
        self.refresh_rate = refresh_rate
        self.console = Console()
        self.live: Optional[Live] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # State tracking
        self.cache = CacheState()
        self.tiers: Dict[str, TierState] = {
            "algorithm": TierState("algorithm"),
            "micro": TierState("micro"),
            "big": TierState("big"),
        }
        
        # Recent throughput history (for sparklines)
        self._throughput_history: Dict[str, deque] = {
            "algorithm": deque(maxlen=60),
            "micro": deque(maxlen=60),
            "big": deque(maxlen=60),
        }
        
        # Callbacks for external updates
        self._on_update: Optional[Callable] = None
    
    def _create_layout(self) -> Layout:
        """Create the dashboard layout."""
        layout = Layout()
        
        # Split into header, main, and footer
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        
        # Main splits into cache (left) and tiers (right)
        layout["main"].split_row(
            Layout(name="cache", ratio=1),
            Layout(name="tiers", ratio=2),
        )
        
        return layout
    
    def _render_header(self) -> Panel:
        """Render the header panel."""
        active_tiers = [t.name for t in self.tiers.values() if t.active]
        status = " | ".join(active_tiers) if active_tiers else "idle"
        
        return Panel(
            f"[bold]Algitex Live Dashboard[/] — Status: {status}",
            style="blue",
        )
    
    def _render_cache_panel(self) -> Panel:
        """Render the cache metrics panel."""
        hit_rate = self.cache.hit_rate
        hit_color = "green" if hit_rate > 0.8 else "yellow" if hit_rate > 0.5 else "red"
        
        content = (
            f"[bold]Cache Stats[/]\n\n"
            f"Entries: {self.cache.entries:,}\n"
            f"Size: {self.cache.size_mb:.2f} MB\n"
            f"Hits: {self.cache.hits:,}\n"
            f"Misses: {self.cache.misses:,}\n"
            f"Hit Rate: [{hit_color}]{hit_rate:.1%}[/{hit_color}]"
        )
        
        return Panel(content, title="[bold]Cache[/]", border_style="green")
    
    def _render_tiers_panel(self) -> Panel:
        """Render the tiers progress panel."""
        table = Table(show_header=True, header_style="bold")
        table.add_column("Tier", style="bold")
        table.add_column("Progress", width=20)
        table.add_column("Status")
        table.add_column("Throughput")
        table.add_column("ETA")
        
        for tier_name, tier in self.tiers.items():
            # Progress bar
            progress_text = f"{tier.current}/{tier.total} ({tier.percent:.0f}%)"
            
            # Status
            if tier.active:
                if tier.current < tier.total:
                    status = "[yellow]running[/]"
                else:
                    status = "[green]done[/]"
            else:
                status = "[dim]idle[/]"
            
            # Throughput sparkline
            if tier.throughput > 1000:
                throughput_str = f"{tier.throughput/1000:.1f}K/s"
            else:
                throughput_str = f"{tier.throughput:.1f}/s"
            
            # ETA
            if tier.eta_seconds > 0:
                if tier.eta_seconds < 60:
                    eta_str = f"{tier.eta_seconds:.0f}s"
                else:
                    eta_str = f"{tier.eta_seconds/60:.1f}m"
            else:
                eta_str = "-"
            
            table.add_row(
                tier.name,
                progress_text,
                status,
                throughput_str,
                eta_str,
            )
        
        return Panel(table, title="[bold]Tiers[/]", border_style="blue")
    
    def _render_footer(self) -> Panel:
        """Render the footer panel."""
        total_processed = sum(t.current for t in self.tiers.values())
        total_success = sum(t.success for t in self.tiers.values())
        total_failed = sum(t.failed for t in self.tiers.values())
        
        content = (
            f"Processed: {total_processed:,} | "
            f"Success: [green]{total_success:,}[/] | "
            f"Failed: [red]{total_failed:,}[/] | "
            f"Press Ctrl+C to exit"
        )
        
        return Panel(content, style="dim")
    
    def _render(self) -> Layout:
        """Render the complete dashboard."""
        layout = self._create_layout()
        
        layout["header"].update(self._render_header())
        layout["cache"].update(self._render_cache_panel())
        layout["tiers"].update(self._render_tiers_panel())
        layout["footer"].update(self._render_footer())
        
        return layout
    
    def _update_loop(self):
        """Background update loop."""
        while self._running:
            if self.live:
                try:
                    self.live.update(self._render())
                except Exception:
                    pass
            
            if self._on_update:
                try:
                    self._on_update()
                except Exception:
                    pass
            
            time.sleep(self.refresh_rate)
    
    def start(self):
        """Start the live dashboard."""
        if self._running:
            return
        
        self._running = True
        
        # Start in a thread for non-blocking operation
        self._thread = threading.Thread(target=self._run_live, daemon=True)
        self._thread.start()
    
    def _run_live(self):
        """Run the live display."""
        with Live(self._render(), console=self.console, refresh_per_second=1/self.refresh_rate) as live:
            self.live = live
            
            while self._running:
                try:
                    live.update(self._render())
                    time.sleep(self.refresh_rate)
                except Exception:
                    break
    
    def stop(self):
        """Stop the live dashboard."""
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=2)
    
    def update_cache_stats(self, hits: Optional[int] = None, misses: Optional[int] = None,
                          entries: Optional[int] = None, size_bytes: Optional[int] = None):
        """Update cache statistics."""
        if hits is not None:
            self.cache.hits = hits
        if misses is not None:
            self.cache.misses = misses
        if entries is not None:
            self.cache.entries = entries
        if size_bytes is not None:
            self.cache.size_bytes = size_bytes
    
    def update_tier_progress(self, tier: str, current: Optional[int] = None,
                            total: Optional[int] = None, success: Optional[int] = None,
                            failed: Optional[int] = None, throughput: Optional[float] = None,
                            active: Optional[bool] = None):
        """Update tier progress."""
        if tier not in self.tiers:
            return
        
        t = self.tiers[tier]
        
        if current is not None:
            t.current = current
        if total is not None:
            t.total = total
        if success is not None:
            t.success = success
        if failed is not None:
            t.failed = failed
        if throughput is not None:
            t.throughput = throughput
            self._throughput_history[tier].append(throughput)
        if active is not None:
            t.active = active
    
    def set_on_update(self, callback: Callable):
        """Set callback for update events."""
        self._on_update = callback
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()


class SimpleProgressTracker:
    """Simplified progress tracking without full dashboard."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        self.tasks: Dict[str, any] = {}
    
    def start(self):
        """Start progress tracking."""
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self.progress.start()
    
    def add_task(self, name: str, total: int) -> str:
        """Add a new progress task."""
        if not self.progress:
            self.start()
        
        task_id = self.progress.add_task(name, total=total)
        self.tasks[name] = task_id
        return task_id
    
    def update(self, name: str, advance: int = 1, completed: Optional[int] = None):
        """Update task progress."""
        if not self.progress or name not in self.tasks:
            return
        
        task_id = self.tasks[name]
        if completed is not None:
            self.progress.update(task_id, completed=completed)
        else:
            self.progress.advance(task_id, advance)
    
    def stop(self):
        """Stop progress tracking."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.tasks.clear()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()


def show_quick_dashboard(duration: float = 10.0):
    """Show a quick demo dashboard for a specified duration."""
    console = Console()
    console.print("[bold]Starting demo dashboard...[/]")
    console.print(f"Running for {duration} seconds. Press Ctrl+C to exit early.\n")
    
    try:
        with LiveDashboard(refresh_rate=0.5) as dashboard:
            # Simulate some activity
            start = time.time()
            while time.time() - start < duration:
                # Simulate cache updates
                dashboard.update_cache_stats(
                    hits=int((time.time() - start) * 10),
                    misses=int((time.time() - start) * 2),
                    entries=50,
                    size_bytes=1024 * 1024,
                )
                
                # Simulate tier progress
                elapsed = time.time() - start
                dashboard.update_tier_progress(
                    "algorithm",
                    current=min(int(elapsed * 10), 100),
                    total=100,
                    throughput=10.0,
                    active=True,
                )
                
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped by user[/]")


if __name__ == "__main__":
    show_quick_dashboard(duration=10.0)
