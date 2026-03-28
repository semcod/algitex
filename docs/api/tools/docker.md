# `tools.docker`

Docker tool manager — spawn, connect, call, teardown.

## Public API

```python
__all__ = ['DockerTool', 'RunningTool', 'DockerToolManager']
```

## Classes

### `DockerTool`

Single Docker-based tool declaration from docker-tools.yaml.

**Methods:**

#### `is_mcp`

```python
def is_mcp(self) -> bool
```

#### `is_rest`

```python
def is_rest(self) -> bool
```

### `RunningTool`

A spawned Docker container with connection info.

### `DockerToolManager`

Spawn Docker containers, connect via MCP/REST, call tools, teardown.

**Methods:**

#### `__init__`

```python
def __init__(self, config: Config)
```

#### `spawn`

```python
def spawn(self, tool_name: str, **overrides) -> RunningTool
```

Start a Docker container for the given tool.

#### `call_tool`

```python
def call_tool(self, tool_name: str, mcp_tool: str, arguments: dict) -> dict
```

Call an MCP tool on a running container.

#### `teardown`

```python
def teardown(self, tool_name: str) -> None
```

Stop and remove container.

#### `teardown_all`

```python
def teardown_all(self) -> None
```

Stop all running containers.

#### `list_tools`

```python
def list_tools(self) -> list[str]
```

List declared tools from docker-tools.yaml.

#### `list_running`

```python
def list_running(self) -> list[str]
```

List currently running tools.

#### `get_capabilities`

```python
def get_capabilities(self, tool_name: str) -> list[str]
```

List MCP tools available on a running container.
