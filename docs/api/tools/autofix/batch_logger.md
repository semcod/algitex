# `tools.autofix.batch_logger`

Markdown logger for batch operations.

Generates structured markdown logs of batch fix operations.


## Functions

### `get_logger`

```python
def get_logger() -> Optional[BatchLogger]
```

Get current logger instance.

### `start_session`

```python
def start_session(backend: str='ollama', batch_size: int=5, parallel: int=3) -> BatchLogger
```

Start new logging session.

### `end_session`

```python
def end_session() -> Optional[str]
```

End session and save log.

## Classes

### `BatchLogEntry`

Single entry in batch log.

### `BatchSessionLog`

Complete log of batch session.

**Methods:**

#### `add_entry`

```python
def add_entry(self, entry: BatchLogEntry) -> None
```

Add entry to log.

#### `finalize`

```python
def finalize(self) -> None
```

Mark session as complete.

#### `to_markdown`

```python
def to_markdown(self) -> str
```

Generate markdown report.
        
        CC: 2 (delegates to 3 render functions)
        Was: CC 22 (complex inline formatting)
        

#### `save`

```python
def save(self, filepath: Optional[str]=None) -> str
```

Save log to file and return path.

### `BatchLogger`

Logger for batch operations with markdown output.

**Methods:**

#### `__init__`

```python
def __init__(self, backend: str='ollama', batch_size: int=5, parallel: int=3)
```

#### `start_group`

```python
def start_group(self, group_idx: int, total_groups: int, category: str, files: list[str]) -> None
```

Start tracking a group.

#### `end_group`

```python
def end_group(self, status: str='success', error: Optional[str]=None) -> None
```

End tracking current group.

#### `set_totals`

```python
def set_totals(self, total_tasks: int, total_groups: int) -> None
```

Set total counts.

#### `finalize`

```python
def finalize(self) -> str
```

Finalize and save log.

#### `print_summary`

```python
def print_summary(self) -> None
```

Print summary to console.
