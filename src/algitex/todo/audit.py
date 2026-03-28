"""Audit and transparency logging for hybrid autofix.

Provides comprehensive logging of all operations with rollback capability.
"""
from __future__ import annotations

import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List
import threading
import getpass
import os


@dataclass
class AuditEntry:
    """Single audit entry for an operation."""
    timestamp: str
    user: str
    operation: str  # 'mechanical_fix', 'llm_fix', 'init', 'rollback'
    file_path: Optional[str] = None
    command: Optional[str] = None  # Exact command executed
    original_content_hash: Optional[str] = None  # For rollback
    changes_summary: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class ChangeRecord:
    """Record of a single file change for rollback."""
    file_path: str
    original_content: str
    new_content_hash: str
    timestamp: str
    operation_id: str


class AuditLogger:
    """Comprehensive audit logging with rollback support.
    
    Usage:
        audit = AuditLogger(".algitex/audit")
        
        # Log operation start
        op_id = audit.start_operation("fix_mechanical", "TODO.md")
        
        # ... make changes ...
        
        # Log with rollback capability
        audit.log_change(file_path, original_content, new_content, op_id)
        audit.complete_operation(op_id, success=True)
        
        # View history
        for entry in audit.get_history():
            print(f"{entry.timestamp}: {entry.operation} by {entry.user}")
        
        # Rollback if needed
        audit.rollback_last()
    """
    
    def __init__(self, audit_dir: str = ".algitex/audit"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.changes_dir = self.audit_dir / "changes"
        self.changes_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self._current_operations: dict[str, AuditEntry] = {}
        
    def _get_user(self) -> str:
        """Get current user info."""
        try:
            return getpass.getuser()
        except:
            return os.environ.get('USER', 'unknown')
    
    def _hash_content(self, content: str) -> str:
        """Generate hash of content for integrity checking."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_op_id(self) -> str:
        """Generate unique operation ID."""
        return f"{int(time.time() * 1000)}-{self._get_user()}"
    
    def start_operation(
        self, 
        operation: str, 
        file_path: Optional[str] = None,
        command: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Start logging an operation.
        
        Returns:
            Operation ID for tracking changes
        """
        op_id = self._generate_op_id()
        
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            user=self._get_user(),
            operation=operation,
            file_path=file_path,
            command=command,
            metadata=metadata or {},
            success=False  # Will be updated on completion
        )
        
        with self._lock:
            self._current_operations[op_id] = entry
            
        self._write_entry(entry, op_id)
        return op_id
    
    def log_change(
        self, 
        file_path: str, 
        original_content: str, 
        new_content: str,
        operation_id: str
    ) -> None:
        """Log a file change with rollback capability."""
        record = ChangeRecord(
            file_path=file_path,
            original_content=original_content,
            new_content_hash=self._hash_content(new_content),
            timestamp=datetime.now().isoformat(),
            operation_id=operation_id
        )
        
        # Save original content for rollback
        change_file = self.changes_dir / f"{operation_id}-{Path(file_path).name}.bak"
        change_file.write_text(original_content, encoding='utf-8')
        
        # Save change record
        meta_file = self.changes_dir / f"{operation_id}-{Path(file_path).name}.json"
        meta_file.write_text(
            json.dumps(asdict(record), indent=2),
            encoding='utf-8'
        )
    
    def complete_operation(
        self, 
        operation_id: str, 
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: float = 0.0
    ) -> None:
        """Complete an operation and finalize log entry."""
        with self._lock:
            if operation_id not in self._current_operations:
                return
                
            entry = self._current_operations[operation_id]
            entry.success = success
            entry.error_message = error_message
            entry.duration_ms = duration_ms
            
            # Update the log file
            self._write_entry(entry, operation_id)
            
            del self._current_operations[operation_id]
    
    def _write_entry(self, entry: AuditEntry, op_id: str) -> None:
        """Write entry to audit log."""
        log_file = self.audit_dir / f"audit-{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        data = asdict(entry)
        data['op_id'] = op_id
        
        with self._lock:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, default=str) + '\n')
    
    def get_history(
        self, 
        limit: int = 100,
        operation: Optional[str] = None,
        user: Optional[str] = None
    ) -> List[AuditEntry]:
        """Get audit history with optional filtering."""
        entries = []
        
        # Read all audit files
        for log_file in sorted(self.audit_dir.glob('audit-*.jsonl'), reverse=True):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    
                    # Apply filters
                    if operation and data.get('operation') != operation:
                        continue
                    if user and data.get('user') != user:
                        continue
                        
                    entries.append(AuditEntry(**data))
                    
                    if len(entries) >= limit:
                        break
                        
            if len(entries) >= limit:
                break
        
        return entries[:limit]
    
    def get_last_operation(self) -> Optional[AuditEntry]:
        """Get the most recent completed operation."""
        history = self.get_history(limit=1)
        return history[0] if history else None
    
    def rollback_operation(self, operation_id: str) -> dict:
        """Rollback a specific operation.
        
        Returns:
            Dict with rollback results: {'restored': [...], 'failed': [...]}
        """
        results = {'restored': [], 'failed': []}
        
        # Find all changes for this operation
        for meta_file in self.changes_dir.glob(f"{operation_id}-*.json"):
            record = json.loads(meta_file.read_text())
            file_path = record['file_path']
            backup_file = meta_file.with_suffix('.bak')
            
            try:
                # Restore original content
                original_content = backup_file.read_text(encoding='utf-8')
                Path(file_path).write_text(original_content, encoding='utf-8')
                results['restored'].append(file_path)
                
                # Clean up backup files
                backup_file.unlink(missing_ok=True)
                meta_file.unlink(missing_ok=True)
                
            except Exception as e:
                results['failed'].append({'file': file_path, 'error': str(e)})
        
        # Log the rollback
        self.start_operation(
            "rollback",
            command=f"rollback {operation_id}",
            metadata={'restored_files': results['restored']}
        )
        
        return results
    
    def rollback_last(self) -> dict:
        """Rollback the most recent operation."""
        last = self.get_last_operation()
        if not last:
            return {'error': 'No operations to rollback'}
        
        # Find operation ID from history
        for log_file in sorted(self.audit_dir.glob('audit-*.jsonl'), reverse=True):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    if data.get('operation') != 'rollback':
                        return self.rollback_operation(data.get('op_id', ''))
        
        return {'error': 'No rollbackable operations found'}
    
    def print_summary(self, limit: int = 10) -> None:
        """Print a human-readable summary of recent operations."""
        print("\n" + "=" * 70)
        print(f"Recent Operations (last {limit})")
        print("=" * 70)
        
        for entry in self.get_history(limit=limit):
            status = "✅" if entry.success else "❌"
            cmd = entry.command or entry.operation
            print(f"{status} {entry.timestamp[:19]} | {entry.user:12} | {cmd[:40]}")
            if entry.file_path:
                print(f"   File: {entry.file_path}")
            if entry.error_message:
                print(f"   Error: {entry.error_message}")
        
        print("=" * 70)
