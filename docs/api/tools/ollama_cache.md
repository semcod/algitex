# `tools.ollama_cache`

LLM Cache layer for OllamaClient — deduplicates identical prompts.

Usage:
    from algitex.tools.ollama_cache import CachedOllamaClient
    
    client = CachedOllamaClient(cache_dir=".algitex/cache")
    # Same prompt + model = cached response, no LLM call


## Classes

### `CacheEntry`

Single cache entry with metadata.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

#### `from_dict`

```python
def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry'
```

### `LLMCache`

Disk-based cache for LLM responses.

**Methods:**

#### `__init__`

```python
def __init__(self, cache_dir: str='.algitex/cache', ttl_hours: float=24.0)
```

#### `get`

```python
def get(self, prompt: str, model: str, **kwargs) -> Optional[CacheEntry]
```

Get cached response if available and not expired.

#### `set`

```python
def set(self, prompt: str, model: str, response: str, tokens_prompt: int=0, tokens_response: int=0, **kwargs) -> None
```

Cache a response.

#### `clear`

```python
def clear(self) -> int
```

Clear all cache entries, return count removed.

#### `stats`

```python
def stats(self) -> Dict[str, Any]
```

Get cache statistics.

#### `list_entries`

```python
def list_entries(self) -> List[Dict[str, Any]]
```

List all cache entries with metadata.

### `CachedOllamaClient(OllamaClient)`

OllamaClient with automatic response caching.

**Methods:**

#### `__init__`

```python
def __init__(self, host: str='http://localhost:11434', timeout: float=120.0, default_model: Optional[str]=None, cache_dir: str='.algitex/cache', cache_ttl_hours: float=24.0, enable_cache: bool=True)
```

#### `generate`

```python
def generate(self, prompt: str, model: Optional[str]=None, **kwargs) -> OllamaResponse
```

Generate with automatic caching.

#### `get_metrics`

```python
def get_metrics(self) -> Dict[str, Any]
```

Get client metrics including cache stats.

#### `clear_cache`

```python
def clear_cache(self) -> int
```

Clear cache and return number of entries removed.
