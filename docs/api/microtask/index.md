# `microtask`

MicroTask API — atomic tasks for small LLMs.

## Public API

```python
__all__ = ['MicroTask', 'MicroTaskBatch', 'TaskType', 'group_tasks_by_file']
```

## Functions

### `group_tasks_by_file`

```python
def group_tasks_by_file(tasks: Iterable[MicroTask]) -> list[MicroTaskBatch]
```

Group micro tasks by file path.

## Classes

### `TaskType(str, Enum)`

Classification tiers for micro tasks.

**Methods:**

#### `tier`

```python
def tier(self) -> int
```

Return the execution tier for this task type.

#### `model_hint`

```python
def model_hint(self) -> str
```

Return a rough model hint for the current tier.

#### `max_context_tokens`

```python
def max_context_tokens(self) -> int
```

Return the soft context budget for this tier.

#### `max_output_tokens`

```python
def max_output_tokens(self) -> int
```

Return the soft output budget for this tier.

### `MicroTask`

Atomic unit of work for a single file change.

**Methods:**

#### `tier`

```python
def tier(self) -> int
```

Return the task tier.

#### `is_algorithmic`

```python
def is_algorithmic(self) -> bool
```

Return True when the task is deterministic.

#### `needs_llm`

```python
def needs_llm(self) -> bool
```

Return True when the task should go through an LLM phase.

#### `span`

```python
def span(self) -> int
```

Return the currently targeted line span.

### `MicroTaskBatch`

Tasks grouped by file for execution.

**Methods:**

#### `algo_tasks`

```python
def algo_tasks(self) -> list[MicroTask]
```

Return deterministic tasks.

#### `llm_tasks`

```python
def llm_tasks(self) -> list[MicroTask]
```

Return non-deterministic tasks.

#### `stats`

```python
def stats(self) -> dict[str, int | str]
```

Return summary statistics for the batch.
