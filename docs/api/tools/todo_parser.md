# `tools.todo_parser`

Todo parser — read tasks from Markdown and text files.

Supports formats:
- GitHub-style: `- [ ] task` / `- [x] task`
- Prefact-style: `file.py:10 - description`
- Plain text lists

Usage:
    from algitex.tools.todo_parser import TodoParser, Task

    parser = TodoParser("TODO.md")
    tasks = parser.parse()  # List of pending Task objects


### `Task`

Single todo task extracted from file.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> dict
```

### `TodoParser`

Parse todo lists from Markdown and text files.

**Methods:**

#### `__init__`

```python
def __init__(self, file_path: str)
```

#### `parse`

```python
def parse(self) -> list[Task]
```

Parse file and return list of pending tasks.

#### `get_stats`

```python
def get_stats(self) -> dict
```

Get statistics about parsed tasks.
