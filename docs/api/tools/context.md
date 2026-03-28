# `tools.context`

Context management — build optimal prompts for LLM coding tools.

## Classes

### `CodeContext`

Assembled context for an LLM coding task.

**Methods:**

#### `to_prompt`

```python
def to_prompt(self, task: str) -> str
```

Convert context to a formatted prompt.

### `ContextBuilder`

Build rich context for LLM coding tasks from .toon files + git + planfile.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str)
```

#### `build`

```python
def build(self, ticket: Optional[Dict[str, Any]]=None, max_tokens: int=8000) -> CodeContext
```

Assemble context from all available sources.

### `SemanticCache`

Optional semantic caching using Qdrant for context retrieval.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str, qdrant_url: str='http://localhost:6333')
```

#### `search_similar_context`

```python
def search_similar_context(self, query: str, limit: int=5) -> List[Dict[str, Any]]
```

Search for similar previous contexts.

#### `store_context`

```python
def store_context(self, context: CodeContext, task: str, result: Dict[str, Any]) -> None
```

Store context with its result for future retrieval.
