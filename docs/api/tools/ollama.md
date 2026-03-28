# `tools.ollama`

Ollama backend — native Ollama support for local LLMs.

Usage:
    from algitex.tools.ollama import OllamaClient
    
    client = OllamaClient()
    models = client.list_models()
    response = client.generate("Explain this code", model="qwen3-coder:latest")


## Classes

### `OllamaModel`

Information about an Ollama model.

**Methods:**

#### `display_name`

```python
def display_name(self) -> str
```

Get display name without tag.

### `OllamaResponse`

Response from Ollama API.

### `OllamaClient`

Client for interacting with Ollama API.

**Methods:**

#### `__init__`

```python
def __init__(self, host: str='http://localhost:11434', timeout: float=120.0, default_model: Optional[str]=None)
```

#### `health`

```python
def health(self) -> bool
```

Check if Ollama is running.

#### `list_models`

```python
def list_models(self) -> List[OllamaModel]
```

List available models.

#### `pull_model`

```python
def pull_model(self, model: str) -> bool
```

Pull a model from Ollama registry.

#### `generate`

```python
def generate(self, prompt: str, model: Optional[str]=None, system: Optional[str]=None, temperature: float=0.7, max_tokens: Optional[int]=None, stream: bool=False, format: Optional[str]=None) -> Union[OllamaResponse, Iterable[OllamaResponse]]
```

Generate text using Ollama.
        
        If stream=True, returns a generator that yields OllamaResponse chunks.
        

#### `chat`

```python
def chat(self, messages: List[Dict[str, str]], model: Optional[str]=None, temperature: float=0.7, max_tokens: Optional[int]=None, stream: bool=False, format: Optional[str]=None) -> Union[OllamaResponse, Iterable[OllamaResponse]]
```

Chat with Ollama using message format.
        
        If stream=True, returns a generator that yields OllamaResponse chunks.
        

#### `fix_code`

```python
def fix_code(self, file_path: str, issue: str, line_number: Optional[int]=None, model: Optional[str]=None) -> Optional[str]
```

Fix code issue using Ollama.

#### `analyze_code`

```python
def analyze_code(self, code: str, model: Optional[str]=None, format: str='json') -> Dict[str, Any]
```

Analyze code and return structured feedback.

#### `close`

```python
def close(self) -> None
```

Close the HTTP client.

### `OllamaService`

High-level service for Ollama operations.

**Methods:**

#### `__init__`

```python
def __init__(self, client: Optional[OllamaClient]=None)
```

#### `ensure_model`

```python
def ensure_model(self, model: str) -> bool
```

Ensure model is available, pull if necessary.

#### `get_recommended_models`

```python
def get_recommended_models(self) -> List[str]
```

Get list of recommended coding models.

#### `auto_fix_file`

```python
def auto_fix_file(self, file_path: str, issue: str, line_number: Optional[int]=None, model: Optional[str]=None) -> bool
```

Fix issue in file and write back the result.
