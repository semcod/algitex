# `tools.autofix.ollama_backend`

Ollama backend for AutoFix.

## Classes

### `OllamaBackend`

Fix issues using Ollama local models.

**Methods:**

#### `__init__`

```python
def __init__(self, service: Optional[OllamaService]=None, model: Optional[str]=None, base_url: str='http://localhost:11434', dry_run: bool=True, timeout: float=DEFAULT_TIMEOUT)
```

#### `fix`

```python
def fix(self, task: Task) -> FixResult
```

Fix a task using Ollama.
