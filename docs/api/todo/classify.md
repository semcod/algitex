# `todo.classify`

Task classification using pattern dispatch.

Replaces complex if/elif chains with a dispatch table for O(1) lookup.


## Public API

```python
__all__ = ['TaskTriage', 'classify_message', 'classify_task', 'KNOWN_MAGIC_CONSTANTS']
```

### `classify_message`

```python
def classify_message(message: str) -> TaskTriage
```

Classify a TODO message using pattern dispatch table.
    
    CC: 4 (1 loop + 3 branches in fallback)
    Was: CC ~50 (25+ if/elif branches)
    

### `classify_task`

```python
def classify_task(task: Any) -> TaskTriage
```

Classify a task-like object.

### `TaskTriage`

Classification result for a single TODO task.

**Methods:**

#### `tier_label`

```python
def tier_label(self) -> str
```

Human-friendly tier label.

#### `is_algorithmic`

```python
def is_algorithmic(self) -> bool
```

Return True for deterministic fixes.

#### `is_micro`

```python
def is_micro(self) -> bool
```

Return True for small-LLM fixes.

#### `is_big`

```python
def is_big(self) -> bool
```

Return True for large-LLM fixes.
