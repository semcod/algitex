# `todo.tiering`

Task tiering and summary helpers for algitex TODO fixes.

## Functions

### `summarise_tasks`

```python
def summarise_tasks(tasks: Iterable[Any]) -> TierSummary
```

Summarise a list of tasks by category and tier.

### `load_todo_tasks`

```python
def load_todo_tasks(todo_path: str | Path='TODO.md') -> list[Task]
```

Parse TODO tasks from a file.

### `filter_tasks`

```python
def filter_tasks(tasks: Iterable[Any]) -> list[Any]
```

Filter tasks by tier and/or category.

### `partition_tasks`

```python
def partition_tasks(tasks: Iterable[Any]) -> dict[str, list[Any]]
```

Partition tasks by tier.

## Classes

### `TierSummary`

Aggregated classification summary for a TODO list.

**Methods:**

#### `add`

```python
def add(self, triage: TaskTriage) -> None
```

Add a classification entry.

#### `algorithmic`

```python
def algorithmic(self) -> int
```

Return algorithmic task count.

#### `micro`

```python
def micro(self) -> int
```

Return small-LLM task count.

#### `big`

```python
def big(self) -> int
```

Return large-LLM task count.

#### `tier_percent`

```python
def tier_percent(self, tier: str) -> int
```

Return integer percentage for a tier.

#### `top_categories`

```python
def top_categories(self, limit: int=12) -> list[tuple[str, int]]
```

Return the most common categories.
