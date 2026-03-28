# `tools.autofix.fallback_backend`

Fallback LLM backend service with automatic failover.

Tries multiple backends in order:
1. LiteLLM Proxy (primary)
2. Ollama (local fallback)
3. Aider (cli fallback)

Usage:
    from algitex.tools.autofix.fallback_backend import FallbackBackend
    
    backend = FallbackBackend(
        primary="litellm-proxy",
        fallbacks=["ollama", "aider"],
        proxy_url="http://localhost:4000"
    )
    result = backend.fix(task)


## Classes

### `BackendStatus`

Status of a backend.

### `FallbackBackend(AutoFixBackend)`

Backend with automatic failover to alternative LLM services.

**Methods:**

#### `__init__`

```python
def __init__(self, primary: str='litellm-proxy', fallbacks: List[str]=None, proxy_url: str='http://localhost:4000', ollama_url: str='http://localhost:11434', model: str='qwen3-coder:latest', timeout: float=30.0, retry_attempts: int=2, dry_run: bool=True)
```

#### `fix`

```python
def fix(self, task: Task) -> FixResult
```

Try to fix task with automatic fallback.

#### `print_status`

```python
def print_status(self)
```

Print status of all backends.
