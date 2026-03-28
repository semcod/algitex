# `tools.parallel.models`

Data models for parallel task coordination — region-based conflict-free execution.

## Classes

### `RegionType(Enum)`

Types of code regions that can be locked.

### `CodeRegion`

An AST-level lockable region within a file.

**Methods:**

#### `key`

```python
def key(self) -> str
```

#### `compute_signature_hash`

```python
def compute_signature_hash(self, source: str) -> str
```

Compute hash of function/class signature to track changes.

### `TaskAssignment`

A ticket assigned to a specific agent with locked regions.

### `MergeResult`

Result of merging agent worktrees back to main.
