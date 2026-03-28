"""Markdown logger for batch operations.

Generates structured markdown logs of batch fix operations.
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BatchLogEntry:
    """Single entry in batch log."""
    timestamp: str
    group_idx: int
    total_groups: int
    category: str
    files: list[str]
    status: str  # success, failed, timeout
    duration_sec: float
    error: Optional[str] = None


@dataclass
class BatchSessionLog:
    """Complete log of batch session."""
    start_time: str
    end_time: Optional[str] = None
    total_tasks: int = 0
    total_groups: int = 0
    batch_size: int = 5
    parallel: int = 3
    backend: str = "ollama"
    entries: list[BatchLogEntry] = field(default_factory=list)
    
    def add_entry(self, entry: BatchLogEntry) -> None:
        """Add entry to log."""
        self.entries.append(entry)
    
    def finalize(self) -> None:
        """Mark session as complete."""
        self.end_time = datetime.now().isoformat()
    
    def to_markdown(self) -> str:
        """Generate markdown report.
        
        CC: 2 (delegates to 3 render functions)
        Was: CC 22 (complex inline formatting)
        """
        header = self._render_header()
        config = self._render_config()
        summary = self._render_summary()
        details = self._render_details()
        
        return f"""# BatchFix Session Log

{header}

## Configuration

{config}

## Summary

{summary}

## Details

{details}
"""

    def _render_header(self) -> str:
        """Render header section with timestamps."""
        start_dt = datetime.fromisoformat(self.start_time) if isinstance(self.start_time, str) else self.start_time
        end_dt = datetime.fromisoformat(self.end_time) if isinstance(self.end_time, str) and self.end_time else None
        
        start_fmt = start_dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(start_dt, datetime) else str(start_dt)
        end_fmt = end_dt.strftime("%Y-%m-%d %H:%M:%S") if end_dt else "In progress..."
        
        return f"""**Started:** {start_fmt}
**Ended:** {end_fmt}"""

    def _render_config(self) -> str:
        """Render configuration table."""
        return f"""| Parameter | Value |
|-----------|-------|
| Backend | {self.backend} |
| Batch Size | {self.batch_size} |
| Parallel Groups | {self.parallel} |
| Total Tasks | {self.total_tasks} |
| Total Groups | {self.total_groups} |"""

    def _render_summary(self) -> str:
        """Render summary statistics table."""
        return f"""| Metric | Count |
|--------|-------|
| Total Entries | {len(self.entries)} |
| Successful | {sum(1 for e in self.entries if e.status == "success")} |
| Failed | {sum(1 for e in self.entries if e.status == "failed")} |
| Timeout | {sum(1 for e in self.entries if e.status == "timeout")} |
| Dry Run | {sum(1 for e in self.entries if e.status == "dry-run")} |
| Total Duration | {sum(e.duration_sec for e in self.entries):.1f}s |"""

    def _render_details(self) -> str:
        """Render details section with all entries."""
        md = ""
        for entry in self.entries:
            status_icon = "✅" if entry.status == "success" else "❌" if entry.status == "failed" else "⏱️" if entry.status == "dry-run" else "⚠️"
            md += f"""### [{entry.group_idx}/{entry.total_groups}] {entry.category}

**Status:** {status_icon} `{entry.status}`
**Duration:** {entry.duration_sec:.1f}s
**Files:**
"""
            for f in entry.files:
                try:
                    rel_path = Path(f).relative_to(Path.cwd())
                    md += f"- `{rel_path}`\n"
                except ValueError:
                    md += f"- `{f}`\n"
            
            if entry.error:
                md += f"""
**Error:**
```
{entry.error}
```
"""
            md += "\n---\n\n"
        
        return md
    
    def save(self, filepath: Optional[str] = None) -> str:
        """Save log to file and return path."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f".algitex/logs/batch_{timestamp}.md"
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown())
        return str(path)


class BatchLogger:
    """Logger for batch operations with markdown output."""
    
    def __init__(self, backend: str = "ollama", batch_size: int = 5, parallel: int = 3):
        self.session = BatchSessionLog(
            start_time=datetime.now().isoformat(),
            backend=backend,
            batch_size=batch_size,
            parallel=parallel
        )
        self._current_group_start: Optional[float] = None
    
    def start_group(self, group_idx: int, total_groups: int, category: str, files: list[str]) -> None:
        """Start tracking a group."""
        self._current_group_start = time.time()
        self._current_group = {
            "group_idx": group_idx,
            "total_groups": total_groups,
            "category": category,
            "files": files
        }
    
    def end_group(self, status: str = "success", error: Optional[str] = None) -> None:
        """End tracking current group."""
        if self._current_group_start is None:
            return
        
        duration = time.time() - self._current_group_start
        
        entry = BatchLogEntry(
            timestamp=datetime.now().isoformat(),
            group_idx=self._current_group["group_idx"],
            total_groups=self._current_group["total_groups"],
            category=self._current_group["category"],
            files=self._current_group["files"],
            status=status,
            duration_sec=duration,
            error=error
        )
        
        self.session.add_entry(entry)
        self._current_group_start = None
    
    def set_totals(self, total_tasks: int, total_groups: int) -> None:
        """Set total counts."""
        self.session.total_tasks = total_tasks
        self.session.total_groups = total_groups
    
    def finalize(self) -> str:
        """Finalize and save log."""
        self.session.finalize()
        return self.session.save()
    
    def print_summary(self) -> None:
        """Print summary to console."""
        print(f"\n{'='*60}")
        print(f"  BATCH LOG SAVED")
        print(f"{'='*60}")
        print(f"  Log file: {self.session.save()}")
        print(f"  Total entries: {len(self.session.entries)}")
        print(f"{'='*60}")


# Global logger instance
_current_logger: Optional[BatchLogger] = None


def get_logger() -> Optional[BatchLogger]:
    """Get current logger instance."""
    return _current_logger


def start_session(backend: str = "ollama", batch_size: int = 5, parallel: int = 3) -> BatchLogger:
    """Start new logging session."""
    global _current_logger
    _current_logger = BatchLogger(backend, batch_size, parallel)
    return _current_logger


def end_session() -> Optional[str]:
    """End session and save log."""
    global _current_logger
    if _current_logger:
        path = _current_logger.finalize()
        _current_logger.print_summary()
        _current_logger = None
        return path
    return None
