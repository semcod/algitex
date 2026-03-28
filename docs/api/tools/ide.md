# `tools.ide`

IDE integration helpers — support for various IDEs and editors.

Usage:
    from algitex.tools.ide import IDEHelper, ClaudeCodeHelper
    
    # Claude Code integration
    claude = ClaudeCodeHelper()
    claude.setup_environment()
    result = claude.fix_file("main.py", "Add type hints")


## Classes

### `IDETool`

IDE tool configuration.

### `IDEHelper`

Base class for IDE integrations.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `check_tool`

```python
def check_tool(self, tool_name: str) -> bool
```

Check if an IDE tool is available.

#### `setup_tool`

```python
def setup_tool(self, tool_name: str) -> bool
```

Setup environment for an IDE tool.

#### `list_tools`

```python
def list_tools(self) -> List[str]
```

List all supported IDE tools.

#### `get_tool_status`

```python
def get_tool_status(self) -> Dict[str, Dict[str, Any]]
```

Get status of all IDE tools.

### `ClaudeCodeHelper(IDEHelper)`

Helper for Claude Code (anthropic-curl) integration.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `setup_environment`

```python
def setup_environment(self) -> Any
```

Setup Claude Code environment for Ollama.

#### `fix_file`

```python
def fix_file(self, file_path: Union[str, Path], instruction: str, model: str='qwen3-coder:latest', dry_run: bool=False) -> bool
```

Fix a file using Claude Code.

#### `chat`

```python
def chat(self, message: str, model: str='qwen3-coder:latest', files: List[Union[str, Path]]=None) -> Optional[str]
```

Chat with Claude Code.

#### `batch_fix`

```python
def batch_fix(self, issues: List[Dict[str, Any]], model: str='qwen3-coder:latest', dry_run: bool=False) -> Dict[str, bool]
```

Fix multiple issues.

### `AiderHelper(IDEHelper)`

Helper for Aider integration.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `fix_file`

```python
def fix_file(self, file_path: Union[str, Path], instruction: str, model: str='qwen3-coder:latest', dry_run: bool=False) -> bool
```

Fix a file using Aider.

### `VSCodeHelper(IDEHelper)`

Helper for VS Code integration.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `open_file`

```python
def open_file(self, file_path: Union[str, Path], line: Optional[int]=None) -> bool
```

Open file in VS Code.

#### `install_extensions`

```python
def install_extensions(self, extensions: List[str]) -> None
```

Install VS Code extensions.

#### `recommended_extensions`

```python
def recommended_extensions(self) -> List[str]
```

Get recommended extensions for algitex workflow.

### `EditorIntegration`

High-level editor integration manager.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `detect_editor`

```python
def detect_editor(self) -> Optional[str]
```

Detect which editor is available.

#### `setup_best_integration`

```python
def setup_best_integration(self) -> str
```

Setup the best available integration.

#### `get_quick_fix_command`

```python
def get_quick_fix_command(self, file_path: str, instruction: str, editor: Optional[str]=None) -> Optional[str]
```

Get a quick fix command for the editor.
