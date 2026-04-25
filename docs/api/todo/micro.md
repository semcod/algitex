# `todo.micro`

Micro-LLM fixes for TODO tasks.

This module extracts the smallest useful code snippet around a TODO task,
feeds it to a local Ollama model, and applies the returned micro-fix back to
source code. It is intentionally conservative: only tasks that map to a single
function or a simple constant-name rewrite are handled here.


### `FunctionSnippet`

Minimal source slice around a function or method.

**Methods:**

#### `line_count`

```python
def line_count(self) -> int
```

Return the number of lines in the snippet.

### `MicroFixResult`

Result of a micro-LLM fix.

### `FunctionExtractor`

Extract a single function or method around a task line.

**Methods:**

#### `extract`

```python
def extract(self, path: Path, line_number: Optional[int]) -> FunctionSnippet | None
```

Return the innermost function/method containing the requested line.

### `MicroPromptBuilder`

Build narrow prompts for micro-LLM fixes.

**Methods:**

#### `build`

```python
def build(self, triage: TaskTriage, snippet: FunctionSnippet, task: Task) -> list[dict[str, str]]
```

Build Ollama chat messages for the given task.

### `MicroFixer`

Execute micro-LLM fixes on a TODO file.

**Methods:**

#### `__init__`

```python
def __init__(self, ollama_url: str='http://localhost:11434', model: str='qwen3-coder:latest', workers: int=4, dry_run: bool=True)
```

#### `fix_file`

```python
def fix_file(self, file_path: Path, tasks: list[Task]) -> list[MicroFixResult]
```

Fix all micro-LLM tasks in a single file.

#### `fix_task`

```python
def fix_task(self, task: Task) -> MicroFixResult
```

Fix a single micro task.

#### `run`

```python
def run(self, todo_path: str | Path='TODO.md', limit: int=0, categories: set[str] | None=None) -> dict[str, int]
```

Run all micro tasks from a TODO file.

#### `fix_tasks_detailed`

```python
def fix_tasks_detailed(self, tasks: list[Task], categories: set[str] | None=None) -> list[MicroFixResult]
```

Run micro fixes on an already-parsed task list and return per-task results.

#### `fix_tasks`

```python
def fix_tasks(self, tasks: list[Task], categories: set[str] | None=None) -> dict[str, int]
```

Run micro fixes on an already-parsed task list.
