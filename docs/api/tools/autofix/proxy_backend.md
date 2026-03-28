# `tools.autofix.proxy_backend`

LiteLLM Proxy backend for AutoFix.

## Classes

### `ProxyBackend`

Fix issues using LiteLLM proxy.

**Methods:**

#### `__init__`

```python
def __init__(self, proxy_url: str='http://localhost:4000', dry_run: bool=False)
```

#### `fix`

```python
def fix(self, task: Task) -> FixResult
```

Fix a task using LiteLLM proxy.
