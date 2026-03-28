# `tools`

Tool discovery — detect which algitex tools are installed.

Each tool is optional. The library works with whatever is available,
gracefully degrading when tools are missing.


## Functions

### `discover_tools`

```python
def discover_tools() -> dict[str, ToolStatus]
```

Check which tools are available.

### `require_tool`

```python
def require_tool(name: str) -> None
```

Raise helpful error if a tool is missing.

### `get_tool_module`

```python
def get_tool_module(name: str) -> Any
```

Import and return a tool module, or None if unavailable.

## Classes

### `ToolStatus`

**Methods:**

#### `emoji`

```python
def emoji(self) -> str
```
