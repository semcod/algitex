# `tools.autofix`

AutoFix — automated code fixing from TODO items.

Refactored: split into backend-specific modules to reduce complexity.

Usage:
    from algitex.tools.autofix import AutoFix

    autofix = AutoFix()
    autofix.fix_all(limit=5)
    autofix.fix_issue("TASK-001")


## Public API

```python
__all__ = ['AutoFix', 'FixResult', 'Task']
```

### `AutoFix`

Automated code fixing using various backends.

**Methods:**

#### `__init__`

```python
def __init__(self, todo_file: str='TODO.md', backend: str='auto', ollama_model: Optional[str]=None, proxy_url: str='http://localhost:4000', dry_run: bool=False)
```

#### `ollama_service`

```python
def ollama_service(self) -> OllamaService
```

Get Ollama service instance.

#### `ollama_backend`

```python
def ollama_backend(self) -> OllamaBackend
```

Get Ollama backend instance.

#### `aider_backend`

```python
def aider_backend(self) -> AiderBackend
```

Get Aider backend instance.

#### `proxy_backend`

```python
def proxy_backend(self) -> ProxyBackend
```

Get Proxy backend instance.

#### `check_backends`

```python
def check_backends(self) -> Dict[str, bool]
```

Check which backends are available.

#### `choose_backend`

```python
def choose_backend(self) -> str
```

Choose the best available backend.

#### `mark_task_done`

```python
def mark_task_done(self, task: Any) -> bool
```

Mark a task as done in TODO.md.

#### `fix_with_ollama`

```python
def fix_with_ollama(self, task: Any) -> FixResult
```

Fix using Ollama.

#### `fix_with_aider`

```python
def fix_with_aider(self, task: Any) -> FixResult
```

Fix using Aider CLI.

#### `fix_with_proxy`

```python
def fix_with_proxy(self, task: Any) -> FixResult
```

Fix using LiteLLM proxy.

#### `fix_task`

```python
def fix_task(self, task: Any, backend: Optional[str]=None) -> FixResult
```

Fix a single task.

#### `fix_all`

```python
def fix_all(self, limit: Optional[int]=None, backend: Optional[str]=None, filter_file: Optional[str]=None) -> List[FixResult]
```

Fix all pending tasks.

#### `fix_issue`

```python
def fix_issue(self, task_id: str, backend: Optional[str]=None) -> Optional[FixResult]
```

Fix a specific task by ID.

#### `print_summary`

```python
def print_summary(self, results: List[FixResult]) -> None
```

Print summary of fixing results.

#### `list_tasks`

```python
def list_tasks(self) -> List[Any]
```

List all pending tasks.

#### `get_stats`

```python
def get_stats(self) -> Dict[str, Any]
```

Get statistics about tasks.
