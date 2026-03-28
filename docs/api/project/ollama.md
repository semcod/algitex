# `project.ollama`

Ollama integration mixins for Project class.

## Classes

### `OllamaMixin`

Ollama integration functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self) -> None
```

#### `check_ollama`

```python
def check_ollama(self) -> dict
```

Check Ollama status and available models.

#### `list_ollama_models`

```python
def list_ollama_models(self) -> list
```

List available Ollama models.

#### `pull_ollama_model`

```python
def pull_ollama_model(self, model: str) -> bool
```

Pull an Ollama model.

#### `generate_with_ollama`

```python
def generate_with_ollama(self, prompt: str, model: Optional[str]=None, system: Optional[str]=None) -> str
```

Generate text using Ollama.
