# `todo.audit`

Audit and transparency logging for hybrid autofix.

Provides comprehensive logging of all operations with rollback capability.


### `AuditEntry`

Single audit entry for an operation.

### `ChangeRecord`

Record of a single file change for rollback.

### `AuditLogger`

Comprehensive audit logging with rollback support.
    
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
    

**Methods:**

#### `__init__`

```python
def __init__(self, audit_dir: str='.algitex/audit')
```

#### `start_operation`

```python
def start_operation(self, operation: str, file_path: Optional[str]=None, command: Optional[str]=None, metadata: Optional[dict]=None) -> str
```

Start logging an operation.
        
        Returns:
            Operation ID for tracking changes
        

#### `log_change`

```python
def log_change(self, file_path: str, original_content: str, new_content: str, operation_id: str) -> None
```

Log a file change with rollback capability.

#### `complete_operation`

```python
def complete_operation(self, operation_id: str, success: bool=True, error_message: Optional[str]=None, duration_ms: float=0.0) -> None
```

Complete an operation and finalize log entry.

#### `get_history`

```python
def get_history(self, limit: int=100, operation: Optional[str]=None, user: Optional[str]=None) -> List[AuditEntry]
```

Get audit history with optional filtering.

#### `get_last_operation`

```python
def get_last_operation(self) -> Optional[AuditEntry]
```

Get the most recent completed operation.

#### `rollback_operation`

```python
def rollback_operation(self, operation_id: str) -> dict
```

Rollback a specific operation.
        
        Returns:
            Dict with rollback results: {'restored': [...], 'failed': [...]}
        

#### `rollback_last`

```python
def rollback_last(self) -> dict
```

Rollback the most recent operation.

#### `print_summary`

```python
def print_summary(self, limit: int=10) -> None
```

Print a human-readable summary of recent operations.
